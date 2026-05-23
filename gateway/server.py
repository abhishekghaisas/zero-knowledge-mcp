import os
import sys
import json
import time
import asyncio
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
from decimal import Decimal # <-- ADD THIS IMPORT
from psycopg2 import pool
from mcp.server.fastmcp import FastMCP

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from src.parser import DefensiveParser, SecurityGateException
from src.logger import AuditLogger

mcp = FastMCP("Zero-Knowledge Gatekeeper Async")

K_THRESHOLD = int(os.getenv("SECURITY_K_THRESHOLD", 25))
guardian = DefensiveParser(mandatory_k_threshold=K_THRESHOLD)
audit_trail = AuditLogger()

db_pool = None
main_event_loop = None 

# ---------------------------------------------------------
# CRITICAL COMPLIANCE FIX: TYPE SERIALIZER EXTENSION
# ---------------------------------------------------------
class DatabaseJsonEncoder(json.JSONEncoder):
    """Intercepts database engine artifacts to format un-serializable objects cleanly."""
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj) # Automatically convert database decimals to standard floats
        return super(DatabaseJsonEncoder, self).default(obj)

def init_database_pool():
    global db_pool
    try:
        db_pool = pool.SimpleConnectionPool(
            minconn=2,
            maxconn=10,
            host=os.getenv("DB_HOST", "phi-db-cluster"),
            database=os.getenv("DB_NAME", "phi_clinical_db"),
            user=os.getenv("DB_USER", "secure_analytics_user"),
            password=os.getenv("DB_PASSWORD", "secure_password")
        )
        print("[*] Successfully provisioned PostgreSQL connection pool (Size: 2-10).")
    except Exception as e:
        print(f"[!] Critical error initializing connection pool: {str(e)}")
        sys.exit(1)

def execute_db_query_sync(query: str):
    global db_pool
    if db_pool is None:
        raise Exception("Database connection pool is uninitialized.")
    conn = db_pool.getconn()
    try:
        with conn.cursor() as cursor:
            cursor.execute(query)
            columns = [desc[0] for desc in cursor.description]
            records = cursor.fetchall()
            return [dict(zip(columns, row)) for row in records]
    finally:
        db_pool.putconn(conn)

async def process_query_logic(clean_query: str) -> str:
    start_time = time.perf_counter()
    try:
        validated_sql = await guardian.validate_query_async(client_id="streamlit_ui_agent", sql_query=clean_query)
        
        loop = asyncio.get_running_loop()
        structured_results = await loop.run_in_executor(None, execute_db_query_sync, validated_sql)
        
        final_results = guardian.enforce_k_anonymity(structured_results)
        duration = (time.perf_counter() - start_time) * 1000
        
        audit_trail.log_transaction(clean_query, "APPROVED", duration, f"Returned {len(final_results)} rows.")
        # CRITICAL FIX: Add our custom encoder class here to stringify Decimals cleanly
        return json.dumps({"status": "success", "data": final_results}, cls=DatabaseJsonEncoder, indent=2)
    except SecurityGateException as sge:
        duration = (time.perf_counter() - start_time) * 1000
        audit_trail.log_transaction(clean_query, "REJECTED_GATE_VIOLATION", duration, str(sge))
        return json.dumps({"status": "rejected", "reason": str(sge)}, indent=2)
    except Exception as e:
        duration = (time.perf_counter() - start_time) * 1000
        audit_trail.log_transaction(clean_query, "SYSTEM_ERROR", duration, str(e))
        return json.dumps({"status": "error", "message": str(e)}, indent=2)

@mcp.tool()
async def execute_aggregated_metric(sql_query: str) -> str:
    return await process_query_logic(sql_query.strip())

class RemoteUIBridgeHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args): return 
    def do_POST(self):
        global main_event_loop
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length).decode('utf-8')
        try:
            req_json = json.loads(post_data)
            query = req_json.get("query", "")
            
            if main_event_loop is None or not main_event_loop.is_running():
                raise Exception("Main asynchronous engine event loop is completely closed or offline.")
            
            future = asyncio.run_coroutine_threadsafe(process_query_logic(query), main_event_loop)
            response_payload = future.result(timeout=10) 
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(response_payload.encode('utf-8'))
        except Exception as e:
            self.send_response(200) 
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "error", "message": str(e)}).encode('utf-8'))

def run_http_bridge():
    server = HTTPServer(('0.0.0.0', 5000), RemoteUIBridgeHandler)
    server.serve_forever()

async def main_async_entry():
    global main_event_loop
    main_event_loop = asyncio.get_running_loop()
    
    threading.Thread(target=run_http_bridge, daemon=True).start()
    print("[*] Threaded UI Bridge Server actively listening on port 5000...")
    
    await mcp.run_sse_async()

if __name__ == "__main__":
    init_database_pool()
    asyncio.run(main_async_entry())