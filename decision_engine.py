def decide(findings):
    """
    Enhanced decision engine with safety guardrails and risk assessment.
    Validates LLM outputs and enforces human approval for critical actions.
    """
    decisions = []

    for f in findings:
        action = "Wait"
        risk = "Low"
        requires_human_approval = True  # Default to safe
        safety_flags = []
        
        # === SAFETY GUARDRAILS ===
        
        # Check for payment-related actions
        cause_lower = f["suspected_cause"].lower()
        is_payment_related = any(keyword in cause_lower for keyword in 
                                  ["payment", "charge", "refund", "transaction", "billing"])
        
        # Check for webhook-related actions
        is_webhook_related = any(keyword in cause_lower for keyword in 
                                 ["webhook", "secret", "callback", "notification"])
        
        # Check for destructive actions
        is_destructive = any(keyword in cause_lower for keyword in 
                            ["delete", "remove", "disable", "revoke", "terminate"])
        
        # Check evidence strength
        evidence_count = (
            len(f.get("evidence_logs", [])) + 
            len(f.get("evidence_docs", [])) + 
            len(f.get("evidence_memory", []))
        )
        weak_evidence = evidence_count < 2
        
        # === PLATFORM-WIDE INCIDENT HANDLING ===
        if f.get("is_platform_incident", False):
            action = "ESCALATE TO ENGINEERING - Platform-wide incident detected"
            risk = "High"
            requires_human_approval = True
            safety_flags.append("PLATFORM-WIDE INCIDENT")
            
            # Block auto-fix for platform incidents
            if f.get("should_block_auto_fix", False):
                safety_flags.append("AUTO-FIX BLOCKED")
        
        # === CRITICAL ACTION DETECTION ===
        elif is_payment_related:
            action = "REQUIRES MANUAL REVIEW - Payment system affected"
            risk = "Critical"
            requires_human_approval = True
            safety_flags.append("PAYMENT-RELATED")
        
        elif is_webhook_related and f["confidence"] > 0.8:
            action = "Send webhook secret fix guide (REQUIRES APPROVAL)"
            risk = "Critical"
            requires_human_approval = True
            safety_flags.append("WEBHOOK-RELATED")
        
        elif is_destructive:
            action = "REQUIRES MANUAL REVIEW - Destructive action detected"
            risk = "Critical"
            requires_human_approval = True
            safety_flags.append("DESTRUCTIVE ACTION")
        
        # === CONFIDENCE-BASED DECISIONS ===
        elif f["confidence"] > 0.9 and not weak_evidence:
            if "missing X-SDK" in f["suspected_cause"]:
                action = "Send setup instructions to merchant"
                risk = "Low"
                requires_human_approval = False  # Safe to auto-execute
            else:
                action = f"Apply fix for: {f['suspected_cause']}"
                risk = "Medium"
                requires_human_approval = True  # High confidence but still needs approval
        
        elif f["confidence"] > 0.7:
            action = "Escalate to engineering for investigation"
            risk = "Medium"
            requires_human_approval = True
        
        elif f["confidence"] > 0.5:
            action = "Escalate to engineering for investigation"
            risk = "Medium"
            requires_human_approval = True
        
        else:
            action = "Collect more data - confidence too low"
            risk = "Low"
            requires_human_approval = True
        
        # === EARLY ESCALATION FROM MEMORY ===
        if f.get("should_escalate_early", False):
            action = f"ESCALATE EARLY - {action} (Previous failures detected)"
            risk = "High" if risk == "Medium" else risk
            safety_flags.append("REPEATED FAILURES")
        
        # === DOWNGRADE CONFIDENCE IF EVIDENCE IS WEAK ===
        if weak_evidence and f["confidence"] > 0.7:
            safety_flags.append("WEAK EVIDENCE")
            risk = "High" if risk == "Medium" else risk
        
        decisions.append({
            "merchant_id": f["merchant_id"],
            "issue": f["ticket"],
            "cause": f["suspected_cause"],
            "confidence": f["confidence"],
            "confidence_before_calibration": f.get("confidence_before_calibration", f["confidence"]),
            "confidence_adjustment": f.get("confidence_adjustment", 0.0),
            "confidence_adjustment_reason": f.get("confidence_adjustment_reason", "N/A"),
            "action": action,
            "risk": risk,
            "requires_human_approval": requires_human_approval,
            "safety_flags": safety_flags,
            
            # Explainability
            "evidence_logs": f.get("evidence_logs", []),
            "evidence_docs": f.get("evidence_docs", []),
            "evidence_memory": f.get("evidence_memory", []),
            "reasoning_chain": f.get("reasoning_chain", []),
            "llm_hypotheses": f.get("llm_hypotheses", []),
            
            # Incident info
            "incident_type": f.get("incident_type", "MERCHANT-SPECIFIC"),
            "is_platform_incident": f.get("is_platform_incident", False),
            "platform_incident_info": f.get("platform_incident_info")
        })

    return decisions
