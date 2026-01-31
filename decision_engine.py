def decide(findings):
    decisions = []

    for f in findings:
        action = "Wait"
        risk = "Low"

        if f["confidence"] > 0.9:
            if "missing X-SDK" in f["suspected_cause"]:
                action = "Send setup instructions to merchant"
                risk = "Low"

            elif "webhook" in f["suspected_cause"]:
                action = "Send webhook secret fix guide"
                risk = "Low"

        elif f["confidence"] > 0.5:
            action = "Escalate to engineering for investigation"
            risk = "Medium"

        else:
            action = "Collect more data"
            risk = "Low"

        decisions.append({
            "merchant_id": f["merchant_id"],
            "issue": f["ticket"],
            "cause": f["suspected_cause"],
            "confidence": f["confidence"],
            "action": action,
            "risk": risk
        })

    return decisions
