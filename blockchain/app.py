import streamlit as st
import pandas as pd
from detect import detect_anomalies
from blockchain import Blockchain

# Page config
st.set_page_config(page_title="Insider Threat Detection", layout="wide")

# Custom CSS for futuristic UI
st.markdown("""
    <style>
    body {
        background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
        color: #f5f5f5;
        font-family: 'Segoe UI', sans-serif;
    }
    .block-container {
        padding: 2rem 3rem;
    }
    .anomaly-card, .block-card {
        background: #111827;
        border: 1px solid #00f2fe;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 0 15px rgba(0,242,254,0.3);
    }
    .stTable {
        border-radius: 8px;
        overflow: hidden;
    }
    table {
        width: 100% !important;
        border-collapse: collapse;
    }
    thead {
        background-color: #00f2fe22;
    }
    tbody tr:nth-child(even) {
        background-color: #1f2937;
    }
    tbody tr:hover {
        background-color: #374151;
    }
    </style>
""", unsafe_allow_html=True)

# Create blockchain
bc = Blockchain()

st.title("Insider Threat Detection with Blockchain")

# Run detection
anomalies = detect_anomalies()

if anomalies:
    st.markdown("<div class='anomaly-card'>", unsafe_allow_html=True)
    st.subheader("Detected Anomalies")

    # Dropdown to select one anomaly
    options = [f"{a['user']} - suspicious activity" for a in anomalies]
    selected = st.selectbox("Select an anomaly to view", options)

    # Find selected anomaly
    chosen = anomalies[options.index(selected)]

    st.subheader("Anomaly Details")
    # Toggle for view mode
    view_mode = st.radio("View Mode", ["Pretty Table", "Raw JSON"], horizontal=True)

    if view_mode == "Pretty Table":
        st.table(pd.DataFrame([chosen]))
    else:
        st.json(chosen)

    # Add anomaly to blockchain
    bc.add_block(chosen)
    st.markdown("</div>", unsafe_allow_html=True)

st.subheader("Blockchain Audit Trail")

# Blockchain blocks UI
for block in bc.chain:
    with st.expander(f"🔗 Block {block.index}", expanded=False):
        st.markdown("<div class='block-card'>", unsafe_allow_html=True)
        st.markdown(f"**Hash:** `{block.hash[:12]}...{block.hash[-6:]}`")
        st.markdown(f"**Prev:** `{block.prev_hash[:12]}...{block.prev_hash[-6:]}`")

        if isinstance(block.data, dict):
            st.json(block.data)
        else:
            st.write(block.data)
        st.markdown("</div>", unsafe_allow_html=True)
