import confidence_calibrator

def execute(decisions):
    """
    Enhanced action executor with explainable reasoning and memory recording.
    """
    print("\n" + "="*80)
    print("🤖 ADVANCED SELF-HEALING AGENT - ACTION PLAN")
    print("="*80 + "\n")
    
    for d in decisions:
        print("─" * 80)
        print(f"🏪 MERCHANT: {d['merchant_id']}")
        print(f"📋 ISSUE: {d['issue']}")
        print()
        
        # === ROOT CAUSE ===
        print(f"🔍 ROOT CAUSE: {d['cause']}")
        print()
        
        # === CONFIDENCE ===
        conf_pct = int(d['confidence'] * 100)
        conf_before_pct = int(d.get('confidence_before_calibration', d['confidence']) * 100)
        adjustment = d.get('confidence_adjustment', 0.0)
        
        if adjustment != 0:
            sign = "+" if adjustment > 0 else ""
            print(f"📊 CONFIDENCE: {conf_pct}% (base: {conf_before_pct}%, {sign}{int(adjustment*100)}%)")
            print(f"   Adjustment reason: {d.get('confidence_adjustment_reason', 'N/A')}")
        else:
            print(f"📊 CONFIDENCE: {conf_pct}%")
        print()
        
        # === INCIDENT TYPE ===
        incident_type = d.get('incident_type', 'MERCHANT-SPECIFIC')
        if incident_type == "PLATFORM-WIDE":
            print("⚠️  INCIDENT TYPE: 🔴 PLATFORM-WIDE")
            if d.get('platform_incident_info'):
                info = d['platform_incident_info']
                print(f"   Pattern: {info.get('pattern', 'Unknown')}")
                print(f"   Affected merchants: {len(info.get('affected_merchants', []))}")
        else:
            print(f"📍 INCIDENT TYPE: {incident_type}")
        print()
        
        # === EXPLAINABLE REASONING ===
        print("🧠 REASONING CHAIN:")
        reasoning = d.get('reasoning_chain', [])
        if reasoning:
            for i, step in enumerate(reasoning, 1):
                print(f"   {i}. {step}")
        else:
            print("   (No reasoning chain available)")
        print()
        
        # === LLM HYPOTHESES ===
        hypotheses = d.get('llm_hypotheses', [])
        if hypotheses:
            print("💡 LLM HYPOTHESES:")
            for i, hyp in enumerate(hypotheses, 1):
                cause = hyp.get('cause', 'Unknown')
                evidence = hyp.get('evidence', 'No evidence')
                print(f"   {i}. {cause}")
                print(f"      Evidence: {evidence}")
            print()
        
        # === EVIDENCE ===
        print("📚 EVIDENCE:")
        
        evidence_logs = d.get('evidence_logs', [])
        if evidence_logs:
            print(f"   From Logs ({len(evidence_logs)}):")
            for log in evidence_logs[:3]:  # Show max 3
                print(f"      • {log}")
        
        evidence_docs = d.get('evidence_docs', [])
        if evidence_docs:
            print(f"   From Documentation ({len(evidence_docs)}):")
            for doc in evidence_docs[:3]:
                print(f"      • {doc}")
        
        evidence_memory = d.get('evidence_memory', [])
        if evidence_memory:
            print(f"   From Memory ({len(evidence_memory)}):")
            for mem in evidence_memory[:2]:
                outcome = mem.get('outcome', 'unknown')
                timestamp = mem.get('timestamp', 'unknown')
                print(f"      • {outcome.upper()} on {timestamp[:10]}")
        
        if not evidence_logs and not evidence_docs and not evidence_memory:
            print("   ⚠️  No evidence available")
        print()
        
        # === PROPOSED ACTION ===
        print(f"⚡ PROPOSED ACTION: {d['action']}")
        print()
        
        # === RISK & SAFETY ===
        risk = d['risk']
        risk_emoji = {
            "Critical": "🔴",
            "High": "🟠",
            "Medium": "🟡",
            "Low": "🟢"
        }.get(risk, "⚪")
        
        print(f"{risk_emoji} RISK LEVEL: {risk}")
        
        safety_flags = d.get('safety_flags', [])
        if safety_flags:
            print(f"🛡️  SAFETY GUARDRAILS TRIGGERED:")
            for flag in safety_flags:
                print(f"   • {flag}")
        print()
        
        # === HUMAN APPROVAL ===
        requires_approval = d.get('requires_human_approval', True)
        if requires_approval:
            print("👤 HUMAN APPROVAL: ✋ REQUIRED")
        else:
            print("👤 HUMAN APPROVAL: ✅ NOT REQUIRED (Safe to auto-execute)")
        
        print("─" * 80)
        print()
    
    print("\n" + "="*80)
    print("📝 All actions require review in the dashboard before execution")
    print("="*80 + "\n")


def record_outcome(merchant_id: str, cause: str, action: str, outcome: str, 
                   confidence_before: float, confidence_after: float):
    """
    Records action outcome to memory for learning.
    This should be called after human approves/rejects an action.
    """
    confidence_calibrator.record_action(
        merchant_id, cause, action, outcome, 
        confidence_before, confidence_after
    )
