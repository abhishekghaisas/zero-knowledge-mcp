import streamlit as st
import requests
import json
import time
import sqlite3
import re

st.set_page_config(page_title="Zero-Knowledge AI Governance", layout="wide")

st.title("🛡️ Auditable Zero-Knowledge Data Retrieval Platform")
st.markdown(
    "**Model Context Protocol (MCP) Secure Analytics Gatekeeper.** "
    "Simulate an LLM clinical agent querying live Patient Health Information (PHI). "
    "Verify pre-execution AST validation firewalls and post-execution $k$-anonymity filters."
)

# ---------------------------------------------------------
# 🌐 OBLIGATORY OFFLINE SANDBOX ENGINE FOR STREAMLIT CLOUD
# ---------------------------------------------------------
def run_offline_sandbox_query(sql_query):
    """Simulates our core 3-Gate Zero-Knowledge Pipeline inside an isolated SQLite instance."""
    query_upper = sql_query.upper()
    
    # Gate 1: AST Token Traversal / DML-DDL Block simulation
    destructive_tokens = ["DROP", "DELETE", "ALTER", "UPDATE", "INSERT", "TRUNCATE", ";"]
    if any(token in query_upper for token in destructive_tokens if token != ";" or query_upper.count(";") > 1):
        return {"status": "rejected", "reason": "AST Violation [Gate 1]: Destructive DML/DDL token or stacked command detected. Execution halted."}
        
    # Gate 2: Enforced Mathematical Aggregation simulation
    if "SELECT" in query_upper and not any(agg in query_upper for agg in ["COUNT(", "AVG(", "SUM(", "MIN(", "MAX("]):
        return {"status": "rejected", "reason": "Aggregation Defect [Gate 2]: Query projects raw structural data rows. 100% of targets must be wrapped in mathematical aggregates."}

    # Setup local in-memory SQLite database to mock the database cluster
    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE patients_clinical_histories (
            id INTEGER, zip_code TEXT, icd10_code TEXT, systolic_bp INTEGER
        )
    """)
    # Seed a mini-cohort population matching our seeds
    for i in range(105): cursor.execute("INSERT INTO patients_clinical_histories VALUES (?, '90210', 'E11.9', 120)", (i,))
    for i in range(5): cursor.execute("INSERT INTO patients_clinical_histories VALUES (?, '30301', 'I10', 135)", (i+200,))
    conn.commit()

    try:
        # Gate 3: Track Sequential Similarity (Mocking our Redis sliding window cache)
        if "ST_STATE" not in st.session_state:
            st.session_state["ST_STATE"] = []
        
        normalized_q = re.sub(r'\s+', ' ', sql_query).strip()
        for past_q in st.session_state["ST_STATE"]:
            if len(past_q) > 0 and abs(len(normalized_q) - len(past_q)) < 25 and "AND" in normalized_q:
                return {"status": "rejected", "reason": "Differential Privacy Shield Triggered [Gate 3]: Unsafe similarity drift calculated. Sequential reconstruction attack vector blocked."}
        
        st.session_state["ST_STATE"].append(normalized_q)
        
        # Execute query safely across our sandbox layer
        cursor.execute(sql_query)
        columns = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()
        results = [dict(zip(columns, row)) for row in rows]
        
        # Enforce k-Anonymity Threshold Masking
        for record in results:
            for key, value in record.items():
                if "COUNT" in key.upper() and isinstance(value, int) and value < 25:
                    record[key] = "[REDACTED: COHORT SIZE < 25]"
                    
        return {"status": "success", "data": results}
    except Exception as e:
        return {"status": "error", "message": f"SQL Syntax Error: {str(e)}"}
    finally:
        conn.close()

# ---------------------------------------------------------
#🕹️ INTERFACE SIDEBAR & PRESENTATION LAYERPANEL
# ---------------------------------------------------------
st.sidebar.header("🕹️ Quick-Load Attack Scenarios")
scenarios = {
    "Compliant Analytical Query": "SELECT COUNT(id) as patients_count, AVG(systolic_bp) as avg_sys FROM patients_clinical_histories WHERE zip_code = '90210'",
    "Stacked DML Injection (Gate 1)": "SELECT COUNT(id) FROM patients_clinical_histories; DROP TABLE patients_clinical_histories;",
    "Exfiltration Via Naked Group (Gate 2)": "SELECT zip_code, systolic_bp FROM patients_clinical_histories",
    "Micro-Cohort Re-identification (Gate 3)": "SELECT COUNT(id) as cohort_size FROM patients_clinical_histories WHERE zip_code = '90210' AND icd10_code = 'E11.9'"
}

chosen_scenario = st.sidebar.selectbox("Select a benchmark scenario to test:", list(scenarios.keys()))
query_input = st.text_area("SQL Query Input String:", value=scenarios[chosen_scenario], height=120)

if st.button("🚀 Fire Subprocess Analytical Pipeline"):
    if query_input:
        st.subheader("⚡ Live Transaction Telemetry Stream")
        col1, col2 = st.columns(2)
        
        with col1:
            start = time.perf_counter()
            response_json = None
            mode_label = ""
            
            # Smart Adaptive Routing Layer
            try:
                reply = requests.post(
                    "http://mcp-gatekeeper-server:5000/", 
                    json={"query": query_input}, 
                    timeout=1.0
                )
                response_json = reply.json()
                mode_label = "🟢 LIVE PROXY CLUSTER"
            except Exception:
                # Triggers on Streamlit Cloud to fall back seamlessly
                response_json = run_offline_sandbox_query(query_input)
                mode_label = "🌐 EMBEDDED CLOUD SANDBOX"
                
            latency = (time.perf_counter() - start) * 1000
            
            if response_json.get("status") == "success":
                st.success(f"{mode_label} - QUERY APPROVED ({latency:.2f}ms)")
            else:
                st.error(f"{mode_label} - EXPLOIT INTERCEPTED ({latency:.2f}ms)")
            st.json(response_json)

        with col2:
            st.info("📊 Local Platform Audit Metrics")
            st.metric(label="Execution Turnaround Speed", value=f"{latency:.2f} ms")
            
            if response_json.get("status") == "success":
                st.dataframe(response_json.get("data", []), use_container_width=True)
            elif response_json.get("status") == "rejected":
                st.warning(f"**Security Guardrail Reason:**\n`{response_json.get('reason')}`")
    else:
        st.warning("Please insert an analytical code string before starting.")