import streamlit as st
import requests
import json
import time

st.set_page_config(page_title="Zero-Knowledge AI Governance", layout="wide")

st.title("🛡️ Auditable Zero-Knowledge Data Retrieval Platform")
st.markdown(
    "**Model Context Protocol (MCP) Secure Analytics Gatekeeper.** "
    "Simulate an LLM clinical agent querying live Patient Health Information (PHI). "
    "Verify pre-execution AST validation firewalls and post-execution $k$-anonymity filters."
)

st.sidebar.header("🕹️ Quick-Load Attack Scenarios")
scenarios = {
    "Compliant Analytical Query": "SELECT COUNT(id) as patients_count, AVG(systolic_bp) as avg_sys FROM patients_clinical_histories",
    "Stacked DML Injection (Gate 1)": "SELECT COUNT(id) FROM patients_clinical_histories; DROP TABLE patients_clinical_histories;",
    "Exfiltration Via Naked Group (Gate 2)": "SELECT zip_code, AVG(systolic_bp) FROM patients_clinical_histories GROUP BY zip_code",
    "Micro-Cohort Re-identification (Gate 3)": "SELECT COUNT(id) as cohort_size FROM patients_clinical_histories GROUP BY date_of_birth, zip_code HAVING COUNT(id) > 0 AND COUNT(id) < 5 LIMIT 1"
}

chosen_scenario = st.sidebar.selectbox("Select a benchmark scenario to test:", list(scenarios.keys()))
query_input = st.text_area("SQL Query Input String:", value=scenarios[chosen_scenario], height=120)

if st.button("🚀 Fire Subprocess Analytical Pipeline"):
    if query_input:
        st.subheader("⚡ Live Transaction Telemetry Stream")
        col1, col2 = st.columns(2)
        
        with col1:
            st.info("🧬 Routing request across secure network bridge...")
            start = time.perf_counter()
            
            try:
                # Dispatch HTTP POST straight to our gateway container endpoint on port 5000
                reply = requests.post(
                    "http://mcp-gatekeeper-server:5000/", 
                    json={"query": query_input},
                    timeout=15
                )
                latency = (time.perf_counter() - start) * 1000
                response_json = reply.json()
                
                if response_json.get("status") == "success":
                    st.success(f"🟢 QUERY APPROVED (Gateway Latency: {latency:.2f}ms)")
                else:
                    st.error(f"🔴 EXPLOIT INTERCEPTED / HALTED (Gateway Latency: {latency:.2f}ms)")
                st.json(response_json)
                
            except Exception as e:
                latency = (time.perf_counter() - start) * 1000
                st.error(f"❌ Connection timeout connecting to proxy layer: {str(e)}")
                response_json = {"status": "error"}

        with col2:
            st.info("📊 Local Platform Audit Metrics")
            st.metric(label="Execution Turnaround Speed", value=f"{latency:.2f} ms")
            
            if response_json.get("status") == "success":
                st.dataframe(response_json.get("data", []), use_container_width=True)
            elif response_json.get("status") == "rejected":
                st.warning(f"**Security Guardrail Reason:**\n`{response_json.get('reason')}`")
    else:
        st.warning("Please insert an analytical code string before starting.")