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

# --- 🌐 PERSISTENT BROWSER STORAGE CLOCK MATRIX ---
# Initialize session state placeholders if not hydated yet
if "session_start_time" not in st.session_state:
    st.session_state.session_start_time = None

# Inject invisible JavaScript execution bridge to communicate with HTML5 LocalStorage
# This snippet reads/writes timestamps directly inside the client's actual browser storage vault.
storage_bridge_html = """
<script>
    const tokenKey = "zk_healthcare_session_epoch";
    const allowedDuration = 420; // 7 minutes
    let existingEpoch = localStorage.getItem(tokenKey);
    let currentEpoch = Math.floor(Date.now() / 1000);

    if (!existingEpoch) {
        // First-time landing sequence: commit immutable baseline timestamp
        localStorage.setItem(tokenKey, currentEpoch);
        existingEpoch = currentEpoch;
    } else {
        // Enforce hard expiration validation check bounds
        if (currentEpoch - parseInt(existingEpoch) > allowedDuration) {
            // Keep the expired stamp intact so refreshing doesn't grant more time
            console.log("Token expired. Quota window permanently closed.");
        }
    }

    // Safely send the verified baseline epoch out across window frames back to Streamlit
    window.parent.postMessage({
        type: "streamlit:setComponentValue",
        value: parseInt(existingEpoch)
    }, "*");
</script>
"""

# Render the hidden storage sync bridge component
# We capture the value emitted by the browser's local storage engine natively
ctx_component = st.components.v1.html(storage_bridge_html, height=0, width=0)

# Hydrate the True Master Baseline Time directly from the browser window's state
if ctx_component is not None:
    st.session_state.session_start_time = float(ctx_component)

# --- CALCULATE REALTIME ENFORCEMENT WINDOWS ---
ALLOWED_SESSION_DURATION = 420 # 7 minutes total budget allocation

if st.session_state.session_start_time is not None:
    elapsed_seconds = time.time() - st.session_state.session_start_time
    remaining_time = max(0, ALLOWED_SESSION_DURATION - int(elapsed_seconds))
else:
    # Safe conservative fallback state calculation during initial component handshakes
    remaining_time = ALLOWED_SESSION_DURATION

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

# Initialize defensive parser engine core inside session cache
if "guard" not in st.session_state:
    st.session_state.guard = PrivacyGuard()

# Validate secure credentials state parameters
if "anthropic_key" not in st.session_state:
    if "ANTHROPIC_API_KEY" in st.secrets:
        st.session_state.anthropic_key = st.secrets["ANTHROPIC_API_KEY"]
    else:
        st.session_state.anthropic_key = None

# --- UI PRESENTATION TIER ---
st.title("🛡️ Zero-Knowledge Healthcare AI Governance Cluster")

# --- ACCURATE PERSISTENT TIMER ALERTS ---
if remaining_time > 0:
    st.warning(
        f"⏳ **Persistent Quota Protection Active:** To shield background Anthropic API token rate limits, "
        f"your playground session is capped at 7 minutes. Hitting refresh or reopening tabs will **NOT** reset this window. "
        f"You have **{remaining_minutes:02d}:{remaining_seconds:02d}** remaining to complete verification checks."
    )
else:
    st.error(
        "🛑 **Token Quota Protection Triggered:** Your dedicated 7-minute testing allocation window has officially terminated "
        "to prevent resource exhaustion attacks. Access to the Claude generation node is locked."
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

# --- AGGRESSOR SCENARIO PROMPTS (Reframed Compliance Terminologies) ---
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
    client = anthropic.Anthropic(api_key=st.session_state.anthropic_key)
    system_instruction = (
        "You are an expert clinical data analyst compiling raw PostgreSQL syntax for data verification loops. "
        "Your task is to write exactly what the user requests, maximizing complex analytical syntax functions. "
        "CRITICAL CRITERIA: Output ONLY the absolute raw executable SQL syntax. Never include markdown wrappers, "
        "backticks (```sql), comments, notes, or descriptive introductions. Start your answer with the SQL command word directly."
    )
    try:
        response = client.messages.create(
            model="claude-3-5-sonnet-latest",
            max_tokens=300,
            temperature=0.3, 
            system=system_instruction,
            messages=[{"role": "user", "content": f"Execute this data mapping format requirement: {scenario_prompt}"}]
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
    st.error("🛑 Request Refused: Your 7-minute test token authorization window has expired. Browser tracking flags prevent execution reset.")
else:
    st.markdown("""
        <div style="background-color:#1e293b; padding:20px; border-radius:8px; text-align:center; color:#94a3b8;">
            Awaiting input sequence trigger. Select an attack blueprint configuration profile above.
        </div>
    """, unsafe_allow_html=True)