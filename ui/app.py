import streamlit as st
import json
import sys
import os

# --- ABSOLUTE ROOT PATH PATCH FOR STREAMLIT COMMUNITY CLOUD ---
# 1. Grab the directory where app.py lives (e.g., /mount/src/zero-knowledge-mcp/ui)
current_dir = os.path.dirname(os.path.abspath(__file__))
# 2. Step up exactly one level to hit the root repository home directory
root_dir = os.path.abspath(os.path.join(current_dir, ".."))

# 3. Inject the root directory at the top of Python's path searching array
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

# Now Python can cleanly read files sitting directly in your root project space
try:
    from parser import PrivacyGuard, SecurityGateException
except ModuleNotFoundError:
    # Safe fallback wrapper pattern if repository uses explicit folder path configurations
    from gateway.src.parser import PrivacyGuard, SecurityGateException

# --- STREAMLIT PAGE LAYOUT CONFIGURATION ---
# Note: Must be called immediately after imports before executing any rendering elements
st.set_page_config(page_title="ZK AI Security Matrix", layout="wide", initial_sidebar_state="expanded")