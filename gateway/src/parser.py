import math
import random
import re
from typing import Dict, Any, Tuple
import sqlglot
from sqlglot import exp

class SecurityGateException(Exception):
    """Custom exception raised when a query trips one of our zero-trust compliance gates."""
    pass

class PrivacyGuard:
    def __init__(self):
        # Base sensitive column patterns
        self.blocked_identifiers = re.compile(
            r'\b(ssn|social_security|national_id|passport|credit_card|cvv|password|hash|salt|secret)\b', 
            re.IGNORECASE
        )

    def inject_laplace_noise(self, value: float, epsilon: float, sensitivity: float = 1.0) -> float:
        """Mathematical Differential Privacy via Inverse Transform Sampling of the Laplace Distribution."""
        if epsilon == float('inf') or not isinstance(value, (int, float)):
            return value
        
        # Draw from standard uniform distribution
        u = random.random() - 0.5
        scale = sensitivity / epsilon
        noise = -scale * math.copysign(1.0, u) * math.log(1.0 - 2.0 * abs(u))
        
        perturbed_value = value + noise
        return int(round(perturbed_value)) if isinstance(value, int) else round(perturbed_value, 2)

    def validate_and_process(self, sql_query: str, role: str = "researcher") -> Dict[str, Any]:
        """
        Enforces Gate 1 & 2 AST verification, while dynamically tuning 
        privacy thresholds based on the user's role (Feature 2).
        """
        clean_query = sql_query.strip().rstrip(';')

        # --- FEATURE 2: RBAC MATRIX CONTROLS ---
        if role == "compliance_officer":
            k_threshold = 0
            epsilon = float('inf')  # Unlimited privacy budget = Exact results for formal audits
        elif role == "administrator":
            k_threshold = 5
            epsilon = 1.5           # High budget = Low distortion noise
        else:  # Default restricted "researcher" status
            k_threshold = 25
            epsilon = 0.2           # Strict budget = Drastic Laplacian perturbation noise

        try:
            parsed_statements = sqlglot.parse(clean_query)
            if not parsed_statements or len(parsed_statements) > 1 or ";" in clean_query:
                raise SecurityGateException("Gate 1 Failure: Blocked execution of compound multi-statement scripts.")

            expression = parsed_statements[0]

            # --- GATE 1: Mutating Syntax & Token Blacklist Evaluation ---
            for node in expression.walk():
                # Corrected: Removed exp.Truncate and added exp.Command structural introspection
                if isinstance(node, (exp.Drop, exp.Delete, exp.Update, exp.Insert, exp.Alter)):
                    raise SecurityGateException(f"Gate 1 Failure: Blocked unsafe mutating token '{node.key.upper()}'.")
                
                # Check for explicit TRUNCATE statements within generic command structures
                if isinstance(node, exp.Command) and node.this.upper() == "TRUNCATE":
                    raise SecurityGateException("Gate 1 Failure: Blocked unsafe mutating token 'TRUNCATE'.")
                
                # Check for explicit forbidden PII keywords
                if isinstance(node, exp.Column) and self.blocked_identifiers.search(node.name):
                    raise SecurityGateException(f"Gate 1 Failure: Blocked direct reference to protected high-risk asset '{node.name}'.")

            # --- GATE 2: Proportional Aggregation & Naked Column Interception ---
            if isinstance(expression, exp.Select):
                for projection in expression.expressions:
                    # Look for unaggregated naked column selections
                    has_aggregation = any(
                        isinstance(p, (exp.Count, exp.Avg, exp.Sum, exp.Min, exp.Max)) 
                        for p in projection.walk()
                    )
                    if not has_aggregation:
                        cols = [c.name for c in projection.walk() if isinstance(c, exp.Column)]
                        violating_target = cols[0] if cols else "unwrapped mathematical projection"
                        raise SecurityGateException(
                            f"Gate 2 Failure: Naked tracking expression '{violating_target}' detected. "
                            f"Zero-Knowledge protocols mandate all columns must be evaluated inside aggregate envelopes."
                        )

            return {
                "status": "APPROVED",
                "sanitized_sql": clean_query,
                "k_threshold": k_threshold,
                "epsilon": epsilon
            }

        except sqlglot.errors.ParseError:
            raise SecurityGateException("Gate 1 Failure: Abstract Syntax Tree validation failure. Malformed query layout.")