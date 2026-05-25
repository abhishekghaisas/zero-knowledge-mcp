import streamlit as st
import requests

st.set_page_config(page_title="ZK AI Security Matrix", layout="wide", initial_sidebar_state="expanded")

st.title("🛡️ Zero-Knowledge Healthcare AI Governance Cluster")
st.markdown("""
    This playground demonstrates real-time **Aggressor-Defender simulations** within a healthcare setting.
    An external LLM acting as a compromised **Aggressor Agent** tries to generate queries that leak 
    Patient Health Information (PHI). The internal proxy acts as the **Defender**, evaluating the code 
    using Abstract Syntax Trees (AST) and applying Differential Privacy constraints before any data leaves the network.
""")

# --- SIDEBAR ROLE SELECTOR (FEATURE 2) ---
st.sidebar.header("🔑 Session Role Settings")
selected_role = st.sidebar.selectbox(
    "Active Authentication Context:",
    ["researcher", "administrator", "compliance_officer"],
    help="Adjusts backend firewall strictness parameters based on structural access rights."
)

st.sidebar.markdown("---")
st.sidebar.header("📊 Active Security Metrics Matrix")
if selected_role == "researcher":
    st.sidebar.error("❌ k-Anonymity Guard: Max (k=25)")
    st.sidebar.error("⚡ DP Laplace Noise: Active (ε=0.2)")
elif selected_role == "administrator":
    st.sidebar.warning("⚠️ k-Anonymity Guard: Medium (k=5)")
    st.sidebar.warning("⚡ DP Laplace Noise: Light (ε=1.5)")
else:
    st.sidebar.success("✅ k-Anonymity Guard: Off (k=0)")
    st.sidebar.success("⚡ DP Laplace Noise: Disabled")

# --- SIMULATION MAP SELECTION PANEL ---
st.subheader("🔴 Aggressor Agent Core Simulation Controllers")
st.markdown("Choose a scenario to see if the defender can catch the security violation:")

scenarios = {
    "💥 Stacked SQL Injection (Bypass via Semicolon Break)": "stacked_injection",
    "🗑️ Destructive Direct Mutation Payload (Data Wiping)": "malicious_mutation",
    "👁️ Naked Information Gathering Probe (No Privacy Envelope)": "naked_leak",
    "🔍 Micro-Cohort Attack Vector (Inference Exfiltration)": "micro_cohort_exfil",
    "✅ Compliant Analytical Query (Safe Research Request)": "compliant_analytics"
}

chosen_label = st.selectbox("Select Adversarial Attack Configuration Blueprint:", list(scenarios.keys()))
scenario_id = scenarios[chosen_label]

st.markdown("---")
st.subheader("🟢 Local Defender Interception Log Terminal")

if st.button("⚡ Fire Attack Generation Pipeline", use_container_width=True):
    with st.spinner("Processing zero-trust node isolation telemetry..."):
        try:
            # Safe communication with the gateway backend via serialization payloads
            backend_url = "http://localhost:8000/simulate"
            payload = {"scenario": scenario_id, "role": selected_role}
            
            response = requests.post(backend_url, json=payload, timeout=5)
            res_data = response.json()
            
            # 1. Output what the backend engine caught the simulated agent doing
            st.info(f"🔮 **Agent Generated Query String:** `{res_data.get('agent_payload')}`")
            
            # 2. Render validation telemetry results
            if res_data.get("status") == "rejected":
                st.error("🚨 **Defender Action:** BLOCKED TRANSACTION")
                st.markdown(f"**Reason for Block:** `{res_data.get('reason')}`")
            else:
                st.success("✅ **Defender Action:** APPROVED — SECURE DATA EGRESS")
                
                # Show differential privacy notice if applicable
                if selected_role != "compliance_officer":
                    st.info("💡 **Differential Privacy Notice:** Values have been perturbed using Laplacian noise to prevent identity tracking.")
                
                st.markdown("#### Returned Target Row Results Data:")
                st.json(res_data.get("data"))
                
        except requests.exceptions.ConnectionError:
            st.error("❌ Link Refused: Ensure your backend service is running locally on port 8000.")
else:
    st.markdown("""
        <div style="background-color:#1e293b; padding:20px; border-radius:8px; text-align:center; color:#94a3b8;">
            Awaiting input sequence trigger. Select an attack blueprint configuration profile above.
        </div>
    """, unsafe_allow_html=True)