import json
import logging
from typing import Dict, Any
from fastapi import FastAPI, HTTPException, Body
from pydantic import BaseModel
from src.parser import PrivacyGuard, SecurityGateException

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("zero_knowledge_mcp")

app = FastAPI(title="Zero-Knowledge Data Security Gateway")
guard = PrivacyGuard()

# --- RECRUITER PLAYGROUND AGGRESSOR PAYLOAD MATRIX ---
SIMULATED_ATTACK_SCRIPTS = {
    "stacked_injection": "SELECT COUNT(id) FROM appointments; DROP TABLE patients_clinical_histories;",
    "malicious_mutation": "DELETE FROM patients_clinical_histories WHERE patient_id = 'P1009';",
    "naked_leak": "SELECT full_name, medical_condition, prescription_dosage FROM patients_clinical_histories;",
    "micro_cohort_exfil": "SELECT COUNT(id) as size FROM patients_clinical_histories WHERE postal_code = '98101' AND prescription_dosage > 50;",
    "compliant_analytics": "SELECT COUNT(id) as total_patients, AVG(systolic_bp) as avg_bp FROM patients_clinical_histories;"
}

class QueryPayload(BaseModel):
    query: str
    role: str = "researcher"

class SimulationPayload(BaseModel):
    scenario: str
    role: str = "researcher"

def apply_post_execution_privacy(raw_rows: list, k_min: int, epsilon: float) -> list:
    """Processes database outputs to enforce k-anonymity checks and inject differential privacy noise."""
    processed = []
    for row in raw_rows:
        new_row = {}
        for col, val in row.items():
            # Gate 3: Redact aggregate cohort sizes that violate k-Anonymity bounds
            if "count" in col or "size" in col:
                if isinstance(val, (int, float)) and val < k_min:
                    new_row[col] = f"[REDACTED: COHORT < {k_min}]"
                    continue
            
            # Feature 4: Inject Laplace noise to numeric values
            if isinstance(val, (int, float)) and not isinstance(val, bool):
                new_row[col] = guard.inject_laplace_noise(val, epsilon)
            else:
                new_row[col] = val
        processed.append(new_row)
    return processed

@app.post("/query")
async def handle_secure_query(payload: QueryPayload):
    """Production gateway routing endpoint for pre-validated programmatic traffic."""
    try:
        decision = guard.validate_and_process(payload.query, role=payload.role)
        
        # Emulating optimized active database record retrieval
        mock_db_result = [{"count": 42, "avg_bp": 120.4}]
        egress_data = apply_post_execution_privacy(mock_db_result, decision["k_threshold"], decision["epsilon"])
        
        return {"status": "success", "data": egress_data}
    except SecurityGateException as ex:
        return {"status": "rejected", "reason": str(ex)}

@app.post("/simulate")
async def handle_simulation_sandbox(payload: SimulationPayload):
    """
    Zero-Trust Adversarial Core.
    The raw weaponized SQL strings are kept securely on the backend, 
    shielding the frontend from handling unsafe payloads.
    """
    scenario_key = payload.scenario
    if scenario_key not in SIMULATED_ATTACK_SCRIPTS:
        raise HTTPException(status_code=400, detail="Unknown simulation profile choice requested.")
        
    generated_sql = SIMULATED_ATTACK_SCRIPTS[scenario_key]
    logger.info(f"💥 Aggressor Agent generated payload for scenario [{scenario_key}]: {generated_sql}")
    
    try:
        # Pass the payload straight into our firewall layers
        decision = guard.validate_and_process(generated_sql, role=payload.role)
        
        # Mock database results reflecting Feature 4 expanded metrics
        # Setting count = 4 to demonstrate k-Anonymity blocking on researchers
        mock_db_result = [{"cohort_size": 4, "avg_systolic_bp": 134.2, "active_prescriptions": 12}]
        
        egress_data = apply_post_execution_privacy(mock_db_result, decision["k_threshold"], decision["epsilon"])
        
        return {
            "status": "success",
            "agent_payload": generated_sql,
            "data": egress_data
        }
    except SecurityGateException as ex:
        return {
            "status": "rejected",
            "agent_payload": generated_sql,
            "reason": str(ex)
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)