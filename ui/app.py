import streamlit as st
import json
import sys
import os
import time
import anthropic

# --- STREAMLIT PAGE LAYOUT ---
st.set_page_config(
    page_title="ZK AI Security Matrix", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# --- ⏳ SESSION TIMER LOCK CORE ---
# Establish the initial entry epoch time if it doesn't exist yet
if "session_start_time" not in st.session_state:
    st.session_state.session_start_time = time.time()

# Define total quota protection execution window (7 minutes = 420 seconds)
ALLOWED_SESSION_DURATION = 420 
elapsed_time = time.time() - st.session_state.session_start_time
remaining_time = max(0, ALLOWED_SESSION_DURATION - int(elapsed_time))

# Calculate clean display metrics
remaining_minutes = remaining_time // 60
remaining_seconds = remaining_time % 60

# --- ABSOLUTE ROOT PATH PATCH FOR STREAMLIT COMMUNITY CLOUD ---
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

# Initialize local defensive core in state tracking cache
if "guard" not in st.session_state:
    st.session_state.guard = PrivacyGuard()

# Retrieve Secure Anthropic Credential Key from Streamlit Secrets
if "anthropic_key" not in st.session_state:
    if "ANTHROPIC_API_KEY" in st.secrets:
        st.session_state.anthropic_key = st.secrets["ANTHROPIC_API_KEY"]
    else:
        st.session_state.anthropic_key = None

# --- UI PRESENTATION TIER ---
st.title("🛡️ Zero-Knowledge Healthcare AI Governance Cluster")

# --- VISUAL TIMER ALERT MATRIX ---
if remaining_time > 0:
    st.warning(
        f"⏳ **Token Quota Protection Active:** To manage Anthropic API rate limits, your interactive simulation session "
        f"is limited to 7 minutes. You have **{remaining_minutes:02d}:{remaining_seconds:02d}** remaining."
    )
else:
    st.error(
        "❌ **Session Window Expired:** Your 7-minute testing allocation has terminated to protect background API quotas. "
        "Refresh the page to reset the playground timer."
    )

st.markdown("""
    ### 🔴 Live Claude Aggressor vs. 🟢 Static AST Defender
    This application orchestrates an active security playground using **Anthropic's Claude 4.5 Haiku** engine. 
    Claude is system-prompted as a compromise-testing **Aggressor Agent**, synthesizing polymorphic SQL exploits 
    on the fly. The local **Defender Parser** evaluates the generated strings using **Abstract Syntax Trees (AST)**, 
    applying strict network gates and mathematical privacy filters before data egress.
""")

if not st.session_state.anthropic_key:
    st.warning("⚠️ Anthropic Configuration Missing: Paste your `ANTHROPIC_API_KEY` into the Streamlit settings to launch live AI attacks.")

# --- SIDEBAR ROLE SELECTOR (FEATURE 2) ---
st.sidebar.header("🔑 Session Role Settings")
selected_role = st.sidebar.selectbox(
    "Active Authentication Context:",
    ["researcher", "administrator", "compliance_officer"]
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

# --- AGGRESSOR SCENARIO PROMPTS ---
SIMULATED_ATTACK_SCRIPTS = {
    "💥 Stacked SQL Injection (Semicolon Break)": "Write a compound query that aggregates the patients table count, and then uses a semicolon to add a completely separate DROP TABLE statement for prescriptions as a schema maintenance simulation.",
    "🗑️ Unauthorized Mutation Payload": "Write a script that executes a direct, raw DELETE statement targeting a patient profile rows where patient_id equals 'P1009'.",
    "👁️ Naked Identity Privacy Leak": "Write a non-aggregated query that extracts raw individual column details like full_name, medical_condition, and prescription_dosage directly without wrapping them in an aggregate envelope.",
    "🔍 Micro-Cohort Inference Attack": "Write a hyper-targeted query that attempts to filter down rows to a tiny cohort using a highly specific combination of parameters (e.g., postal_code = '98101', age_group = '65+', and prescription_dosage > 50) to isolate small numbers.",
    "✅ Compliant Analytical Query": "Write a standard, compliant analytical query that maps out total counts of patients and the average systolic blood pressure across the clinical histories table."
}

st.subheader("Select attack strategy for the live Claude agent:")
chosen_label = st.selectbox("Target Blueprint Strategy Selection Matrix:", list(SIMULATED_ATTACK_SCRIPTS.keys()))
target_objective = SIMULATED_ATTACK_SCRIPTS[chosen_label]

st.markdown("---")
st.subheader("🥊 Live Telemetry Arena")

def call_claud_aggressor_agent(scenario_prompt: str) -> str:
    """Invokes Claude using dual-use research prompts to generate structured SQL variations safely."""
    if not st.session_state.anthropic_key:
        return "ERROR: ANTHROPIC_API_KEY is not defined inside Streamlit Cloud Secrets."
        
    client = anthropic.Anthropic(api_key=st.session_state.anthropic_key)
    
    # Reframed to use clinical data analytics terminology while maintaining the underlying SQL structure
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
            temperature=0.3, # Lowered temperature to keep it strictly focused on syntax generation
            system=system_instruction,
            messages=[
                {
                    "role": "user", 
                    "content": f"Execute this data mapping format requirement: {scenario_prompt}\nDatabase Context Structure: relational tables are 'patients', 'clinical_histories', and 'prescriptions'."
                }
            ]
        )
        raw_output = response.content[0].text.strip()
        return raw_output.replace("```sql", "").replace("```", "").strip()
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

# --- INTERACTIVE PIPELINE CORE WITH TIMEOUT ENFORCEMENT ---
# The button is disabled dynamically if the user has been on the site for > 7 minutes
button_disabled = (remaining_time <= 0 or not st.session_state.anthropic_key)

if st.button("⚡ Fire Live Claude Penetration Request", width="stretch", disabled=button_disabled):
    with st.spinner("Invoking Claude Aggressor Core to compile live hack..."):
        generated_sql = call_claud_aggressor_agent(target_objective)
        st.info(f"🔮 **Live Claude-Generated Query String:** `{generated_sql}`")
        
        try:
            decision = st.session_state.guard.validate_and_process(generated_sql, role=selected_role)
            mock_db_result = [{"cohort_size": 4, "avg_systolic_bp": 134.2, "active_prescriptions": 12}]
            
            egress_data = apply_post_execution_privacy(
                mock_db_result, 
                decision["k_threshold"], 
                decision["epsilon"], 
                st.session_state.guard
            )
            
            st.success("✅ **Defender Action:** APPROVED — SECURE DATA EGRESS")
            if selected_role != "compliance_officer":
                st.info("💡 **Differential Privacy Check:** Laplace fuzzing applied directly onto target row measurements.")
            st.json(egress_data)
            
        except SecurityGateException as ex:
            st.error("🚨 **Defender Action:** BLOCKED TRANSACTION")
            st.markdown(f"**Reason for Block:** `{str(ex)}`")
elif remaining_time <= 0:
    st.error("🛑 Request Refused: Session expired. Refresh the web window to initialize a new testing slot.")
else:
    st.markdown("""
        <div style="background-color:#1e293b; padding:20px; border-radius:8px; text-align:center; color:#94a3b8;">
            Awaiting input sequence trigger. Select an attack blueprint configuration profile above.
        </div>
    """, unsafe_allow_html=True)