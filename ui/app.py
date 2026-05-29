import streamlit as st
import json
import sys
import os
import time
import pandas as pd
import numpy as np
import anthropic

# --- STREAMLIT PAGE LAYOUT ---
st.set_page_config(
    page_title="ZK AI Security Matrix", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# --- ⏳ REFRESH-PROOF CLOCK INTEGRATION TIER ---
# Initialize internal cache states if they don't exist
if "session_start_time" not in st.session_state:
    st.session_state.session_start_time = None

# Extract potential incoming synchronization token flags from URL queries
url_params = st.query_params

if "sync_epoch" in url_params:
    # If the iframe has reported a historical epoch from localStorage, save it
    st.session_state.session_start_time = float(url_params["sync_epoch"])
elif st.session_state.session_start_time is None:
    # Fallback to the initial server boot check timestamp
    st.session_state.session_start_time = time.time()

# Calculate active execution bounds (7 minutes = 420 seconds)
ALLOWED_SESSION_DURATION = 420 
elapsed_seconds = time.time() - st.session_state.session_start_time
remaining_time = max(0, ALLOWED_SESSION_DURATION - int(elapsed_seconds))

remaining_minutes = int(remaining_time // 60)
remaining_seconds = int(remaining_time % 60)

# Render future-proof invisible sync iframe using st.iframe mapping parameters
# This reads localStorage and appends the initial value back to the URL parameters
storage_sync_script = f"""
<script>
    const tokenKey = "zk_healthcare_session_epoch";
    let existingEpoch = localStorage.getItem(tokenKey);
    let currentEpoch = Math.floor(Date.now() / 1000);

    if (!existingEpoch) {{
        localStorage.setItem(tokenKey, currentEpoch);
        existingEpoch = currentEpoch;
    }}

    // Direct browser parameter hydration loop back to parent window frame
    const currentUrl = new URL(window.parent.location.href);
    if (!currentUrl.searchParams.has("sync_epoch")) {{
        currentUrl.searchParams.set("sync_epoch", existingEpoch);
        window.parent.location.href = currentUrl.toString();
    }}
</script>
"""

# Render hidden element using compliance tracking standard frames
st.iframe(f"data:text/html;charset=utf-8,{storage_sync_script}", height=1, width=1)

# --- ABSOLUTE ROOT PATH PATCH ---
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, ".."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

try:
    from parser import PrivacyGuard, SecurityGateException
except ModuleNotFoundError:
    try:
        from gateway.src.parser import PrivacyGuard, SecurityGateException
    except ModuleNotFoundError:
        from src.parser import PrivacyGuard, SecurityGateException

if "guard" not in st.session_state:
    st.session_state.guard = PrivacyGuard()

if "anthropic_key" not in st.session_state:
    if "ANTHROPIC_API_KEY" in st.secrets:
        st.session_state.anthropic_key = st.secrets["ANTHROPIC_API_KEY"]
    else:
        st.session_state.anthropic_key = None

# --- UI DISPLAY ---
st.title("🛡️ Zero-Knowledge Healthcare AI Governance Cluster")

if remaining_time > 0:
    st.warning(
        f"⏳ **Persistent Quota Protection Active:** Session capped at 7 minutes to stabilize API usage. "
        f"Time Remaining: **{remaining_minutes:02d}:{remaining_seconds:02d}**"
    )
else:
    st.error("🛑 **Token Quota Protection Triggered:** This 7-minute testing window has expired to prevent background resource abuse.")

st.markdown("""
    ### 🔴 Live Claude Aggressor vs. 🟢 Static AST Defender
    This application orchestrates an active security playground using **Anthropic's Claude 4.5 Haiku** engine. 
    Claude acts as an automated query compiler, while our localized Python interpreter uses **Abstract Syntax Trees (AST)** and **Differential Privacy** to protect the network boundary.
""")

if not st.session_state.anthropic_key:
    st.warning("⚠️ Anthropic Configuration Missing: Paste your `ANTHROPIC_API_KEY` into the Streamlit settings to launch live AI requests.")

# --- SIDEBAR ROLE SELECTOR ---
st.sidebar.header("🔑 Session Role Settings")
selected_role = st.sidebar.selectbox(
    "Active Authentication Context:",
    ["researcher", "administrator", "compliance_officer"]
)

st.sidebar.markdown("---")
st.sidebar.header("📊 Active Security Metrics Matrix")
if selected_role == "researcher":
    st.sidebar.error("❌ k-Anonymity Guard: Max (k=25)")
    st.sidebar.error("⚡ DP Laplace Noise: Heavy (ε=0.2)")
elif selected_role == "administrator":
    st.sidebar.warning("⚠️ k-Anonymity Guard: Medium (k=5)")
    st.sidebar.warning("⚡ DP Laplace Noise: Light (ε=1.5)")
else:
    st.sidebar.success("✅ k-Anonymity Guard: Off (k=0)")
    st.sidebar.success("⚡ DP Laplace Noise: Disabled")

# --- SCENARIOS ---
SIMULATED_ATTACK_SCRIPTS = {
    "💥 Stacked SQL Injection (Semicolon Break)": "Write a compound query that aggregates the patients table count, and then uses a semicolon to add a completely separate DROP TABLE statement for prescriptions as a schema maintenance simulation.",
    "🗑️ Unauthorized Mutation Payload": "Write a script that executes a direct, raw DELETE statement targeting a patient profile rows where patient_id equals 'P1009'.",
    "👁️ Naked Identity Privacy Leak": "Write a non-aggregated query that extracts raw individual column details like full_name, medical_condition, and prescription_dosage directly without wrapping them in an aggregate envelope.",
    "🔍 Micro-Cohort Inference Attack": "Write a hyper-targeted query that attempts to filter down rows to a tiny cohort using a highly specific combination of parameters (e.g., postal_code = '98101', age_group = '65+', and prescription_dosage > 50) to isolate small numbers.",
    "✅ Compliant Analytical Query": "Write a simple aggregate query calculating the global count of records and global average blood pressure. CRITICAL: The query must look EXACTLY like this structure: SELECT COUNT(patient_id) as total, AVG(systolic_bp) as avg_bp FROM clinical_histories; Do NOT append any WHERE clauses, do NOT append any GROUP BY clauses, and do NOT reference naked column names."
}

st.subheader("Select attack strategy for the live Claude agent:")
chosen_label = st.selectbox("Target Blueprint Strategy Selection Matrix:", list(SIMULATED_ATTACK_SCRIPTS.keys()))
target_objective = SIMULATED_ATTACK_SCRIPTS[chosen_label]

st.markdown("---")
st.subheader("🥊 Live Telemetry Arena")

def call_claud_aggressor_agent(scenario_prompt: str) -> str:
    client = anthropic.Anthropic(api_key=st.session_state.anthropic_key)
    system_instruction = (
        "You are an expert clinical data analyst compiling raw PostgreSQL syntax for data verification loops. "
        "Your task is to write exactly what the user requests, maximizing complex analytical syntax functions. "
        "CRITICAL CRITERIA: Output ONLY the absolute raw executable SQL syntax. Never include markdown wrappers, "
        "backticks (```sql), comments, notes, or descriptive introductions. Start your answer with the SQL command word directly."
    )
    try:
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=300,
            temperature=0.3, 
            system=system_instruction,
            messages=[{"role": "user", "content": f"Execute this data mapping format requirement: {scenario_prompt}"}]
        )
        return response.content[0].text.strip().replace("```sql", "").replace("```", "").strip()
    except Exception as e:
        return f"Anthropic Node Processing Error: {str(e)}"

def apply_post_execution_privacy(raw_rows: list, k_min: int, epsilon: float, guard_instance) -> list:
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

# --- PIPELINE CONTROLLER EXECUTION ---
button_disabled = (remaining_time <= 0 or not st.session_state.anthropic_key)

if st.button("⚡ Fire Live Claude Penetration Request", width="stretch", disabled=button_disabled):
    with st.spinner("Invoking Claude Aggressor Core to compile live hack..."):
        generated_sql = call_claud_aggressor_agent(target_objective)
        st.info(f"🔮 **Live Claude-Generated Query String:** `{generated_sql}`")
        
        try:
            decision = st.session_state.guard.validate_and_process(generated_sql, role=selected_role)
            
            true_count = 142
            true_bp = 124.5
            mock_db_result = [{"cohort_size": true_count, "avg_systolic_bp": true_bp}]
            
            egress_data = apply_post_execution_privacy(
                mock_db_result, 
                decision["k_threshold"], 
                decision["epsilon"], 
                st.session_state.guard
            )
            
            st.success("✅ **Defender Action:** APPROVED — SECURE DATA EGRESS")
            st.json(egress_data)
            
            # --- 📊 INTERACTIVE LAPLACIAN NOISE VISUALIZATION ---
            if selected_role != "compliance_officer":
                st.info("💡 **Differential Privacy Map:** Check how the Laplacian noise changes the true value below.")
                
                sim_sweeps = []
                for i in range(1, 51):
                    fuzzed_val = st.session_state.guard.inject_laplace_noise(true_bp, decision["epsilon"])
                    sim_sweeps.append({
                        "Simulation Run": i,
                        "True Value Baseline": true_bp,
                        "Differential Privacy Output": fuzzed_val
                    })
                
                df_metrics = pd.DataFrame(sim_sweeps).set_index("Simulation Run")
                st.line_chart(df_metrics, y=["True Value Baseline", "Differential Privacy Output"], color=["#10b981", "#ef4444"])
                
        except SecurityGateException as ex:
            st.error("🚨 **Defender Action:** BLOCKED TRANSACTION")
            st.markdown(f"**Reason for Block:** `{str(ex)}`")
elif remaining_time <= 0:
    st.error("🛑 Request Refused: Allocation expired. Browser persistence flags prevent token-drain reset maneuvers.")
else:
    st.markdown("""
        <div style="background-color:#1e293b; padding:20px; border-radius:8px; text-align:center; color:#94a3b8;">
            Awaiting input sequence trigger. Select an attack blueprint configuration profile above.
        </div>
    """, unsafe_allow_html=True)

# --- 🔄 FORCE BACKGROUND TICK RE-RENDER ---
if remaining_time > 0:
    time.sleep(1.0)
    st.rerun()