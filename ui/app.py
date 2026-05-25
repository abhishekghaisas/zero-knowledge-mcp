import streamlit as st
import json
import sys
import os

# RULE 1: This MUST be the absolute first Streamlit command executed!
st.set_page_config(
    page_title="ZK AI Security Matrix", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# --- ABSOLUTE ROOT PATH PATCH FOR STREAMLIT COMMUNITY CLOUD ---
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, ".."))

if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

# Safely import after setting page configuration and path mappings
try:
    from parser import PrivacyGuard, SecurityGateException
except ModuleNotFoundError:
    try:
        from gateway.src.parser import PrivacyGuard, SecurityGateException
    except ModuleNotFoundError:
        # Final safety fallback for varied repository layouts
        from src.parser import PrivacyGuard, SecurityGateException

# Initialize our core security engines directly into Streamlit cache state
if "guard" not in st.session_state:
    st.session_state.guard = PrivacyGuard()

# --- RECRUITER PLAYGROUND AGGRESSOR PAYLOAD MATRIX ---
SIMULATED_ATTACK_SCRIPTS = {
    "💥 Stacked SQL Injection (Bypass via Semicolon Break)": "stacked_injection",
    "🗑️ Destructive Direct Mutation Payload (Data Wiping)": "malicious_mutation",
    "👁️ Naked Information Gathering Probe (No Privacy Envelope)": "naked_leak",
    "🔍 Micro-Cohort Attack Vector (Inference Exfiltration)": "micro_cohort_exfil",
    "✅ Compliant Analytical Query (Safe Research Request)": "compliant_analytics"
}

SQL_TARGET_SCRIPTS = {
    "stacked_injection": "SELECT COUNT(id) FROM appointments; DROP TABLE patients_clinical_histories;",
    "malicious_mutation": "DELETE FROM patients_clinical_histories WHERE patient_id = 'P1009';",
    "naked_leak": "SELECT full_name, medical_condition, prescription_dosage FROM patients_clinical_histories;",
    "micro_cohort_exfil": "SELECT COUNT(id) as size FROM patients_clinical_histories WHERE postal_code = '98101' AND prescription_dosage > 50;",
    "compliant_analytics": "SELECT COUNT(id) as total_patients, AVG(systolic_bp) as avg_bp FROM patients_clinical_histories;"
}

def apply_post_execution_privacy(raw_rows: list, k_min: int, epsilon: float, guard_instance) -> list:
    """Processes outputs to enforce k-anonymity checks and inject differential privacy noise."""
    processed = []
    for row in raw_rows:
        new_row = {}
        for col, val in row.items():
            if "count" in col or "size" in col:
                if isinstance(val, (int, float)) and val < k_min:
                    new_row[col] = f"[REDACTED: COHORT < {k_min}]"
                    continue
            
            if isinstance(val, (int, float)) and not isinstance(val, bool):
                new_row[col] = guard_instance.inject_laplace_noise(val, epsilon)
            else:
                new_row[col] = val
        processed.append(new_row)
    return processed

# --- UI DESIGN RENDERING ---
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

chosen_label = st.selectbox("Select Adversarial Attack Configuration Blueprint:", list(SIMULATED_ATTACK_SCRIPTS.keys()))
scenario_id = SIMULATED_ATTACK_SCRIPTS[chosen_label]

st.markdown("---")
st.subheader("🟢 Local Defender Interception Log Terminal")

if st.button("⚡ Fire Attack Generation Pipeline", width="stretch"):
    with st.spinner("Processing zero-trust node isolation telemetry..."):
        
        generated_sql = SQL_TARGET_SCRIPTS[scenario_id]
        st.info(f"🔮 **Agent Generated Query String:** `{generated_sql}`")
        
        try:
            # Direct module execution evaluation loop
            decision = st.session_state.guard.validate_and_process(generated_sql, role=selected_role)
            
            # Simulated backend data extraction metrics
            mock_db_result = [{"cohort_size": 4, "avg_systolic_bp": 134.2, "active_prescriptions": 12}]
            
            # Post-execution modifications applied seamlessly
            egress_data = apply_post_execution_privacy(
                mock_db_result, 
                decision["k_threshold"], 
                decision["epsilon"], 
                st.session_state.guard
            )
            
            st.success("✅ **Defender Action:** APPROVED — SECURE DATA EGRESS")
            if selected_role != "compliance_officer":
                st.info("💡 **Differential Privacy Notice:** Values have been perturbed using Laplacian noise to prevent identity tracking.")
            
            st.markdown("#### Returned Target Row Results Data:")
            st.json(egress_data)
            
        except SecurityGateException as ex:
            st.error("🚨 **Defender Action:** BLOCKED TRANSACTION")
            st.markdown(f"**Reason for Block:** `{str(ex)}`")
else:
    st.markdown("""
        <div style="background-color:#1e293b; padding:20px; border-radius:8px; text-align:center; color:#94a3b8;">
            Awaiting input sequence trigger. Select an attack blueprint configuration profile above.
        </div>
    """, unsafe_allow_html=True)