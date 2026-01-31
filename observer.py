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

def main():
    print("\n=== SELF-HEALING SUPPORT AGENT ===\n")

    rules = load_docs()
    logs = load_logs()
    tickets = load_tickets()

    findings = analyze(tickets, logs, rules)
    decisions = decide(findings)
    execute(decisions)

if __name__ == "__main__":
    main()
