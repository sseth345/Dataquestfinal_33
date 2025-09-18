import streamlit as st
from detect import detect_anomalies
from blockchain import Blockchain

# Create blockchain
bc = Blockchain()

st.title("🚨 Insider Threat Detection with Blockchain")

# Run detection
anomalies = detect_anomalies()

if anomalies:
    st.subheader("Detected Anomalies")

    # Dropdown to select one anomaly
    options = [f"{a['user']} - suspicious activity" for a in anomalies]
    selected = st.selectbox("Select an anomaly to view", options)

    # Find selected anomaly
    chosen = anomalies[options.index(selected)]

    # Display details
    st.json(chosen)

    # Add to blockchain
    bc.add_block(chosen)

st.subheader("📜 Blockchain Audit Trail")
for block in bc.chain:
    st.write(f"Index: {block.index}")
    st.write(f"Hash: {block.hash[:12]}...")
    st.write(f"Prev: {block.prev_hash[:12]}...")
    st.markdown("---")
