import json
import llm_reasoner
import incident_detector
import confidence_calibrator

def analyze(tickets, logs, rules_text):
    """
    Enhanced analysis with dual intelligence: rule-based + LLM reasoning.
    Includes cross-merchant incident detection and memory-weighted confidence.
    """
    findings = []
    
    # First, detect cross-merchant patterns
    incident_info = incident_detector.detect_patterns(logs)
    
    for ticket in tickets:
        merchant = ticket["merchant_id"]
        issue = ticket["subject"]
        message = ticket["message"]

        merchant_logs = [l for l in logs if l["merchant_id"] == merchant]

        # === RULE-BASED REASONING (Deterministic) ===
        rule_based_cause = "Unknown"
        rule_based_confidence = 0.3
        evidence_logs = []
        evidence_docs = []

        for log in merchant_logs:
            if "X-SDK-Version" in log["message"]:
                rule_based_cause = "Merchant missing X-SDK-Version header"
                rule_based_confidence = 0.95
                evidence_logs.append(log["message"])
                evidence_docs.append("Rule #1: All checkout API requests must include X-SDK-Version header")

            elif "webhook" in log["message"].lower() or "secret" in log["message"].lower():
                rule_based_cause = "Merchant using wrong webhook secret (should be B)"
                rule_based_confidence = 0.9
                evidence_logs.append(log["message"])
                evidence_docs.append("Rule #2: Headless webhooks use Secret Key B (not A)")

            elif log["error_code"] >= 500:
                rule_based_cause = "Possible platform instability"
                rule_based_confidence = 0.6
                evidence_logs.append(f"Error {log['error_code']}: {log['message']}")
                evidence_docs.append("Rule #4: Headless API has stricter rate limits, 500 errors may indicate platform issues")

        # === LLM REASONING (Probabilistic) ===
        llm_result = llm_reasoner.reason(ticket, merchant_logs, rules_text)
        
        # Merge rule-based and LLM reasoning
        if llm_result:
            # LLM provided additional insights
            suspected_cause = llm_result["selected_cause"]
            base_confidence = llm_result["confidence"]
            reasoning_chain = llm_result["reasoning_chain"]
            
            # Merge evidence
            evidence_logs.extend(llm_result.get("evidence_logs", []))
            evidence_docs.extend(llm_result.get("evidence_docs", []))
            
            # Add LLM hypotheses to reasoning
            llm_hypotheses = llm_result.get("hypotheses", [])
        else:
            # Fall back to rule-based reasoning
            suspected_cause = rule_based_cause
            base_confidence = rule_based_confidence
            reasoning_chain = [
                "Step 1: Analyzed logs using deterministic rules",
                f"Step 2: Matched pattern: {rule_based_cause}",
                f"Step 3: Confidence based on rule certainty: {rule_based_confidence}"
            ]
            llm_hypotheses = []

        # === MEMORY-WEIGHTED CONFIDENCE CALIBRATION ===
        calibration = confidence_calibrator.adjust_confidence(
            merchant, 
            suspected_cause, 
            base_confidence
        )
        
        final_confidence = calibration["adjusted_confidence"]
        memory_evidence = calibration.get("memory_evidence", [])
        
        # === CHECK IF MERCHANT IS IN PLATFORM-WIDE INCIDENT ===
        is_platform_incident = incident_detector.check_merchant_in_incident(merchant, incident_info)
        
        findings.append({
            "merchant_id": merchant,
            "ticket": issue,
            "suspected_cause": suspected_cause,
            "confidence": final_confidence,
            "confidence_before_calibration": base_confidence,
            "confidence_adjustment": calibration["adjustment"],
            "confidence_adjustment_reason": calibration["reason"],
            "log_count": len(merchant_logs),
            
            # Explainability
            "evidence_logs": list(set(evidence_logs)),  # Remove duplicates
            "evidence_docs": list(set(evidence_docs)),
            "evidence_memory": memory_evidence,
            "reasoning_chain": reasoning_chain,
            "llm_hypotheses": llm_hypotheses,
            
            # Incident detection
            "incident_type": incident_info["incident_type"] if is_platform_incident else "MERCHANT-SPECIFIC",
            "is_platform_incident": is_platform_incident,
            "platform_incident_info": incident_info if is_platform_incident else None,
            
            # Safety flags
            "should_escalate_early": calibration["should_escalate_early"],
            "should_block_auto_fix": incident_info["should_block_auto_fix"] if is_platform_incident else False
        })

    return findings
