"""
Test script to demonstrate platform-wide incident detection.
This temporarily swaps in test data to show the cross-merchant pattern detection.
"""

from brain import analyze
from decision_engine import decide
from action import execute
import json
import csv
from pathlib import Path

BASE = Path(".")

def load_docs():
    with open(BASE / "docs" / "headless_guide.md", "r") as f:
        return f.read()

def load_test_logs():
    """Load test logs with platform-wide incident"""
    with open(BASE / "logs" / "api_activity_platform_test.json", "r") as f:
        return json.load(f)

def load_test_tickets():
    """Load test tickets for platform-wide incident"""
    tickets = []
    with open(BASE / "tickets" / "inbox_platform_test.csv", newline='', encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            tickets.append(row)
    return tickets

def main():
    print("\n" + "="*80)
    print("🧪 PLATFORM-WIDE INCIDENT DETECTION TEST")
    print("="*80)
    print("\nThis test demonstrates cross-merchant pattern detection.")
    print("Scenario: 12 merchants experiencing 500 errors within 1 minute")
    print("="*80 + "\n")

    rules = load_docs()
    logs = load_test_logs()
    tickets = load_test_tickets()

    print(f"Loaded {len(tickets)} tickets and {len(logs)} log entries\n")

    findings = analyze(tickets, logs, rules)
    decisions = decide(findings)
    execute(decisions)

if __name__ == "__main__":
    main()
