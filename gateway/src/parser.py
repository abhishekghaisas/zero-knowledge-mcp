import os
import json
import sqlglot
from sqlglot import expressions
import redis.asyncio as aioredis

class SecurityGateException(Exception):
    """Custom exception routed directly to the audit log pipeline."""
    pass

class DefensiveParser:
    def __init__(self, mandatory_k_threshold: int = 5, min_edit_distance: int = 12):
        self.k_threshold = mandatory_k_threshold
        self.min_edit_distance = min_edit_distance

        #Connecting to sandboxed Redis container in network
        self.redis_host = os.getenv("REDIS_HOST", "7-alpine")
        self.redis_port = int(os.getenv("REDIS_PORT", 6379))
        self.redis = aioredis.Redis(host=self.redis_host, port=self.redis_port, decode_responses=True)

        self.forbidden_tokens = {
            "drop", "insert", "update", "delete", "alter", "create", "truncate", "merge"
        }
        self.allowed_aggregates = {
            "count", "avg", "sum", "min", "max", "stddev", "variance"
        }

    def _calculate_levenshtein(self, s1: str, s2: str) -> int:
        """Computes the standard edit distance metrics between two strings."""
        if len(s1) < len(s2):
            return self._calculate_levenshtein(s2, s1)
        if len(s2) == 0:
            return len(s1)

        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row

        return previous_row[-1]

    async def validate_query_async(self, client_id: str, sql_query: str) -> str:
        """
        Executes deep structural AST inspection across normalized query representations.
        Enforces Differential Privacy rules by tracking consecutive query edits.
        """
        normalized_query = " ".join(sql_query.strip().lower().split())
        redis_key = f"mcp:history:{client_id}"

        past_queries = await self.redis.lrange(redis_key, 0, -1)

        # --- RECURSIVE COUNTER-ATTACK: DIFFERENTIAL DISTANCE CHECK ---
        for past_query in past_queries:
            distance = self._calculate_levenshtein(normalized_query, past_query)
            if 0 < distance < self.min_edit_distance:
                raise SecurityGateException(
                    f"Differential Privacy Shield Triggered: Input query structure exhibits an unsafe "
                    f"similarity drift (Levenshtein Distance: {distance} < Threshold: {self.min_edit_distance}). "
                    f"Sequential reconstruction attack vector suspected."
                )

        try:
            # GATE 1: Multi-statement & Mutation Protections
            parsed_statements = sqlglot.parse(sql_query, read="postgres")
            if len(parsed_statements) > 1 or ";" in sql_query.strip().rstrip(";"):
                raise SecurityGateException("Gate 1 Violation: Multi-statement execution detected.")
            
            expression = parsed_statements[0]
            if not expression:
                raise SecurityGateException("Gate 1 Violation: Evaluated AST is null or invalid.")

            for node in expression.walk():
                node_type = type(node).__name__.lower()
                if any(forbidden in node_type for forbidden in self.forbidden_tokens):
                    raise SecurityGateException("Gate 1 Violation: Write/Mutation command token detected.")

            # GATE 2: Deep Projection Enforcements
            all_select_nodes = list(expression.find_all(expressions.Select))
            if not all_select_nodes:
                raise SecurityGateException("Gate 2 Violation: Command structure must contain a valid SELECT block.")

            for select_node in all_select_nodes:
                for projection in select_node.expressions:
                    if isinstance(projection, expressions.Star):
                        continue
                        
                    has_aggregate = False
                    for child in projection.walk():
                        if isinstance(child, expressions.Anonymous) and child.name.lower() in self.allowed_aggregates:
                            has_aggregate = True
                            break
                        elif isinstance(child, expressions.Func) and child.sql_name().lower() in self.allowed_aggregates:
                            has_aggregate = True
                            break
                            
                    if not has_aggregate:
                        raise SecurityGateException(
                            f"Gate 2 Violation: Naked expression '{projection}' exposed within statement block. "
                            f"All projections must be wrapped in mathematical aggregate envelopes."
                        )
            
            # Push query out to shared state list and trim window to last 5 entries
            async with self.redis.pipeline(transaction=True) as pipe:
                await(pipe.lpush(redis_key, normalized_query).ltrim(redis_key,0,4).expire(redis_key, 3600).execute())
            return sql_query

        except sqlglot.errors.ParseError as pe:
            raise SecurityGateException(f"Gate 1 Violation: Malformed SQL structural parsing failed: {str(pe)}")

    def enforce_k_anonymity(self, records: list) -> list:
        sanitized_records = []
        for row in records:
            violates_k = False
            for key, val in row.items():
                if isinstance(val, int) and 0 < val < self.k_threshold:
                    violates_k = True
                    break
            if violates_k:
                redacted_row = {key: f"[REDACTED: COHORT SIZE < {self.k_threshold}]" for key in row.keys()}
                sanitized_records.append(redacted_row)
            else:
                sanitized_records.append(row)
        return sanitized_records