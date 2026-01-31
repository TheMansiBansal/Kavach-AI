def execute(decisions):
    print("\n--- AGENT ACTION PLAN ---\n")

    for d in decisions:
        print(f"Merchant {d['merchant_id']}")
        print(f" Issue: {d['issue']}")
        print(f" Root Cause: {d['cause']}")
        print(f" Confidence: {int(d['confidence']*100)}%")
        print(f" Proposed Action: {d['action']}")
        print(f" Risk Level: {d['risk']}")
        print(" Human Approval Required: YES")
        print("-" * 40)
