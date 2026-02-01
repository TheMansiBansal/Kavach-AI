# Kavach-AI: Advanced Self-Healing Agent

An Advanced Track-level agentic AI platform for headless commerce migration support with LLM reasoning, cross-merchant incident detection, memory-based learning, and comprehensive safety guardrails.

Cyber Cypher 5.0 - Team: Bejeweled Bits - Mansi Bansal, Aakanksha Desai, Adhitri Satish

## Features

**Dual Intelligence System**
- Rule-based reasoning for deterministic patterns
- LLM-powered reasoning (Gemini API) for complex analysis
- Multi-hypothesis generation and root cause selection

**Cross-Merchant Incident Detection**
- Identifies platform-wide issues (10+ merchants in 10 min)
- Blocks auto-fixes for platform incidents
- Automatic escalation to engineering

**Memory-Weighted Confidence**
- Learns from past successes and failures
- Boosts confidence for proven solutions
- Early escalation for repeated failures

**Explainable Reasoning**
- Full evidence chains from logs, docs, and memory
- Step-by-step reasoning display
- LLM hypothesis tracking

**Safety Guardrails**
- Blocks auto-execution for payments, webhooks, destructive actions
- Multi-level risk assessment (Critical/High/Medium/Low)
- Confidence downgrade for weak evidence


## Architecture

The system follows the **Observe → Reason → Decide → Act → Learn** loop:

- **Observer** - Ingests tickets (CSV) and logs (JSON)
- **Brain** - Dual intelligence: rule-based + LLM reasoning
- **Incident Detector** - Cross-merchant pattern analysis
- **Confidence Calibrator** - Memory-weighted adjustments
- **Decision Engine** - Safety guardrails and risk assessment
- **Action Executor** - Explainable output and memory recording
- **Dashboard** - Streamlit control room with approval workflow


## Key Modules

| Module | Purpose |
|--------|---------|
| `llm_reasoner.py` | LLM-powered hypothesis generation |
| `incident_detector.py` | Cross-merchant pattern detection |
| `confidence_calibrator.py` | Memory-weighted confidence |
| `brain.py` | Dual intelligence orchestration |
| `decision_engine.py` | Safety guardrails |
| `action.py` | Explainable output |
| `dashboard.py` | Streamlit control room |
| `memory.json` | Persistent learning store |

## Safety

The agent does not auto-execute:
- Payment-related actions
- Webhook configuration changes
- Destructive operations

All critical actions require human approval in the dashboard.
