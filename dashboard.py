import streamlit as st
import json
import csv
from pathlib import Path
from brain import analyze
from decision_engine import decide
import action

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

st.set_page_config(page_title="Advanced Self-Healing Agent", layout="wide")

st.title("🧠 Advanced Self-Healing Support Control Room")
st.subheader("AI-Powered Headless Migration Intelligence")

# Load data
rules = load_docs()
logs = load_logs()
tickets = load_tickets()

# Analyze
findings = analyze(tickets, logs, rules)
decisions = decide(findings)

# === PLATFORM-WIDE INCIDENT OVERVIEW ===
platform_incidents = [d for d in decisions if d.get('is_platform_incident', False)]
if platform_incidents:
    st.error("🚨 PLATFORM-WIDE INCIDENT DETECTED")
    incident_info = platform_incidents[0].get('platform_incident_info', {})
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Affected Merchants", len(incident_info.get('affected_merchants', [])))
    col2.metric("Incident Type", incident_info.get('incident_type', 'Unknown'))
    col3.metric("Priority", incident_info.get('escalation_priority', 'HIGH'))
    
    st.warning(f"**Pattern:** {incident_info.get('pattern', 'Unknown pattern')}")
    st.info("⚠️ Auto-fixes have been BLOCKED for all affected merchants. Engineering escalation required.")
    st.divider()

# === MERCHANT INCIDENTS ===
st.markdown("## 🔍 Active Merchant Incidents")

for d in decisions:
    with st.container():
        # Header with key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        col1.metric("Merchant", d["merchant_id"])
        col2.metric("Issue", d["issue"])
        
        # Confidence with color coding
        conf_pct = int(d['confidence'] * 100)
        conf_delta = d.get('confidence_adjustment', 0.0)
        if conf_delta != 0:
            col3.metric("Confidence", f"{conf_pct}%", f"{int(conf_delta*100)}%")
        else:
            col3.metric("Confidence", f"{conf_pct}%")
        
        # Risk with color
        risk = d['risk']
        risk_color = {
            "Critical": "🔴",
            "High": "🟠",
            "Medium": "🟡",
            "Low": "🟢"
        }.get(risk, "⚪")
        col4.metric("Risk", f"{risk_color} {risk}")
        
        # Incident type
        incident_type = d.get('incident_type', 'MERCHANT-SPECIFIC')
        if incident_type == "PLATFORM-WIDE":
            st.error(f"**Incident Type:** 🔴 PLATFORM-WIDE")
        else:
            st.info(f"**Incident Type:** {incident_type}")
        
        # Root cause
        st.markdown(f"**🔍 Root Cause:** {d['cause']}")
        
        # Proposed action
        st.markdown(f"**⚡ Proposed Action:** {d['action']}")
        
        # Safety flags
        safety_flags = d.get('safety_flags', [])
        if safety_flags:
            st.warning(f"**🛡️ Safety Guardrails:** {', '.join(safety_flags)}")
        
        # === EXPLAINABLE REASONING (Expandable) ===
        with st.expander("🧠 View Reasoning & Evidence"):
            # Reasoning chain
            st.markdown("**Reasoning Chain:**")
            reasoning = d.get('reasoning_chain', [])
            if reasoning:
                for i, step in enumerate(reasoning, 1):
                    st.markdown(f"{i}. {step}")
            else:
                st.markdown("_No reasoning chain available_")
            
            st.markdown("---")
            
            # LLM Hypotheses
            hypotheses = d.get('llm_hypotheses', [])
            if hypotheses:
                st.markdown("**💡 LLM Hypotheses:**")
                for i, hyp in enumerate(hypotheses, 1):
                    cause = hyp.get('cause', 'Unknown')
                    evidence = hyp.get('evidence', 'No evidence')
                    st.markdown(f"{i}. **{cause}**")
                    st.markdown(f"   - Evidence: {evidence}")
            
            st.markdown("---")
            
            # Evidence sections
            col_a, col_b, col_c = st.columns(3)
            
            with col_a:
                st.markdown("**📊 Evidence from Logs:**")
                evidence_logs = d.get('evidence_logs', [])
                if evidence_logs:
                    for log in evidence_logs[:5]:
                        st.markdown(f"- {log}")
                else:
                    st.markdown("_None_")
            
            with col_b:
                st.markdown("**📚 Evidence from Docs:**")
                evidence_docs = d.get('evidence_docs', [])
                if evidence_docs:
                    for doc in evidence_docs[:5]:
                        st.markdown(f"- {doc}")
                else:
                    st.markdown("_None_")
            
            with col_c:
                st.markdown("**🧠 Evidence from Memory:**")
                evidence_memory = d.get('evidence_memory', [])
                if evidence_memory:
                    for mem in evidence_memory[:3]:
                        outcome = mem.get('outcome', 'unknown')
                        timestamp = mem.get('timestamp', 'unknown')[:10]
                        st.markdown(f"- {outcome.upper()} on {timestamp}")
                else:
                    st.markdown("_None_")
            
            # Confidence adjustment
            if d.get('confidence_adjustment', 0.0) != 0:
                st.markdown("---")
                st.markdown(f"**📊 Confidence Adjustment:** {d.get('confidence_adjustment_reason', 'N/A')}")
        
        # === HUMAN APPROVAL ===
        st.markdown("---")
        
        requires_approval = d.get('requires_human_approval', True)
        if requires_approval:
            st.warning("👤 **Human Approval Required**")
        else:
            st.success("✅ **Safe to Auto-Execute**")
        
        col_approve, col_reject = st.columns(2)
        
        with col_approve:
            if st.button(f"✅ Approve {d['merchant_id']}", key=f"approve_{d['merchant_id']}"):
                # Record success to memory
                action.record_outcome(
                    d['merchant_id'],
                    d['cause'],
                    d['action'],
                    "success",
                    d.get('confidence_before_calibration', d['confidence']),
                    d['confidence']
                )
                st.success(f"✅ Action approved for {d['merchant_id']} and recorded to memory")
                st.rerun()
        
        with col_reject:
            if st.button(f"❌ Reject {d['merchant_id']}", key=f"reject_{d['merchant_id']}"):
                # Record failure to memory
                action.record_outcome(
                    d['merchant_id'],
                    d['cause'],
                    d['action'],
                    "failure",
                    d.get('confidence_before_calibration', d['confidence']),
                    d['confidence']
                )
                st.error(f"❌ Action rejected for {d['merchant_id']} and recorded to memory")
                st.rerun()
        
        st.divider()

# === SYSTEM STATUS ===
st.markdown("---")
st.markdown("## 📊 System Status")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Active Tickets", len(tickets))
col2.metric("Total Decisions", len(decisions))
col3.metric("High Risk", len([d for d in decisions if d['risk'] in ['Critical', 'High']]))
col4.metric("Platform Incidents", len(platform_incidents))
