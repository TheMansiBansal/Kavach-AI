import json

def analyze(tickets, logs, rules_text):
    findings = []

    for ticket in tickets:
        merchant = ticket["merchant_id"]
        issue = ticket["subject"]
        message = ticket["message"]

        merchant_logs = [l for l in logs if l["merchant_id"] == merchant]

        root_cause = "Unknown"
        confidence = 0.3

        for log in merchant_logs:
            if "X-SDK-Version" in log["message"]:
                root_cause = "Merchant missing X-SDK-Version header"
                confidence = 0.95

            elif "webhook" in log["message"].lower() or "secret" in log["message"].lower():
                root_cause = "Merchant using wrong webhook secret (should be B)"
                confidence = 0.9

            elif log["error_code"] >= 500:
                root_cause = "Possible platform instability"
                confidence = 0.6

        findings.append({
            "merchant_id": merchant,
            "ticket": issue,
            "suspected_cause": root_cause,
            "confidence": confidence,
            "log_count": len(merchant_logs)
        })

    return findings
