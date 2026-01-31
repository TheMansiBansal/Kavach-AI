import streamlit as st
import json
import csv
from pathlib import Path
from brain import analyze
from decision_engine import decide

BASE = Path(".")

def load_docs():
    with open(BASE / "docs" / "headless_guide.md", "r") as f:
        return f.read()

def load_logs():
    with open(BASE / "logs" / "api_activity.json", "r") as f:
        return json.load(f)

def load_tickets():
    tickets = []
    with open(BASE / "tickets" / "inbox.csv", newline='', encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            tickets.append(row)
    return tickets

st.set_page_config(page_title="Self-Healing Support Agent", layout="wide")

st.title("🧠 Self-Healing Support Control Room")
st.subheader("Live Headless Migration Intelligence")

rules = load_docs()
logs = load_logs()
tickets = load_tickets()

findings = analyze(tickets, logs, rules)
decisions = decide(findings)

st.markdown("## 🔍 Active Merchant Incidents")

for d in decisions:
    with st.container():
        col1, col2, col3, col4 = st.columns(4)

        col1.metric("Merchant", d["merchant_id"])
        col2.metric("Issue", d["issue"])
        col3.metric("Confidence", f"{int(d['confidence']*100)}%")
        col4.metric("Risk", d["risk"])

        st.markdown(f"**Root Cause:** {d['cause']}")
        st.markdown(f"**Proposed Action:** {d['action']}")

        a = st.button(f"Approve {d['merchant_id']}")
        r = st.button(f"Reject {d['merchant_id']}")

        if a:
            st.success(f"Action approved for {d['merchant_id']}")
        if r:
            st.warning(f"Action rejected for {d['merchant_id']}")

        st.divider()
