import os
import json
import logging
from datetime import datetime

class AuditLogger:
    def __init__(self, log_dir: str = "/app/logs", log_filename: str = "audit.jsonl"):
        """
        Initializes an unbuffered JSONL (JSON Lines) compliance logger.
        JSONL structure ensures logs can be natively parsed by ingestion engines like ELK or Splunk.
        """
        self.log_path = os.path.join(log_dir, log_filename)
        
        # Ensure the mounted directory exists
        os.makedirs(log_dir, exist_ok=True)
        
        # Configure the internal logging utility
        self.logger = logging.getLogger("SystemAuditTrail")
        self.logger.setLevel(logging.INFO)
        
        # Avoid duplicate handlers if re-instantiated
        if not self.logger.handlers:
            handler = logging.FileHandler(self.log_path, encoding="utf-8")
            formatter = logging.Formatter('%(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

    def log_transaction(self, raw_query: str, status: str, execution_time_ms: float = 0.0, details: str = ""):
        """
        Pushes a structured security ledger entry out to the persistent storage envelope.
        """
        payload = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "evaluated_query": raw_query,
            "security_status": status,  # 'APPROVED', 'REJECTED_GATE_VIOLATION', 'SYSTEM_ERROR'
            "latency_ms": round(execution_time_ms, 2),
            "telemetry_details": details
        }
        
        # Force a single line string format and write immediately
        self.logger.info(json.dumps(payload))