import json
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

MEMORY_FILE = Path(".") / "memory.json"

def load_memory() -> Dict:
    """Load memory from memory.json"""
    if not MEMORY_FILE.exists():
        return {"actions": []}
    
    try:
        with open(MEMORY_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return {"actions": []}


def save_memory(memory: Dict):
    """Save memory to memory.json"""
    try:
        with open(MEMORY_FILE, "w") as f:
            json.dump(memory, indent=2, fp=f)
    except Exception as e:
        print(f"Failed to save memory: {e}")


def adjust_confidence(merchant_id: str, suspected_cause: str, base_confidence: float) -> Dict:
    """
    Adjusts confidence based on historical memory.
    
    Args:
        merchant_id: Merchant ID
        suspected_cause: Root cause hypothesis
        base_confidence: Initial confidence (0-1)
    
    Returns:
        Dictionary with:
        - adjusted_confidence: New confidence score
        - adjustment: How much was added/subtracted
        - reason: Explanation of adjustment
        - should_escalate_early: Boolean flag
        - memory_evidence: List of relevant past actions
    """
    
    memory = load_memory()
    actions = memory.get("actions", [])
    
    # Find relevant past actions for this merchant + cause combination
    exact_matches = []
    merchant_matches = []
    cause_matches = []
    
    for action in actions:
        if action["merchant_id"] == merchant_id and action["cause"].lower() == suspected_cause.lower():
            exact_matches.append(action)
        elif action["merchant_id"] == merchant_id:
            merchant_matches.append(action)
        elif action["cause"].lower() == suspected_cause.lower():
            cause_matches.append(action)
    
    adjustment = 0.0
    reason = "No historical data"
    should_escalate_early = False
    memory_evidence = []
    
    # Priority 1: Exact merchant + cause matches
    if exact_matches:
        successes = [a for a in exact_matches if a["outcome"] == "success"]
        failures = [a for a in exact_matches if a["outcome"] == "failure"]
        
        if successes and not failures:
            # Previously successful - boost confidence significantly
            adjustment = 0.3
            reason = f"Previously successful {len(successes)} time(s) for this merchant + cause"
            memory_evidence = successes[-3:]  # Last 3 successes
            
        elif failures and not successes:
            # Previously failed - reduce confidence and escalate
            adjustment = -0.2
            reason = f"Previously failed {len(failures)} time(s) for this merchant + cause"
            should_escalate_early = True
            memory_evidence = failures[-3:]  # Last 3 failures
            
        elif successes and failures:
            # Mixed results - slight boost if more successes
            success_rate = len(successes) / len(exact_matches)
            if success_rate > 0.6:
                adjustment = 0.15
                reason = f"Mixed results: {len(successes)} successes, {len(failures)} failures (60%+ success rate)"
            else:
                adjustment = -0.1
                reason = f"Mixed results: {len(successes)} successes, {len(failures)} failures (<60% success rate)"
                should_escalate_early = True
            memory_evidence = exact_matches[-3:]
    
    # Priority 2: Same merchant, different cause
    elif merchant_matches:
        recent_failures = [a for a in merchant_matches[-5:] if a["outcome"] == "failure"]
        if len(recent_failures) >= 3:
            # This merchant has had multiple recent failures - be cautious
            adjustment = -0.1
            reason = f"Merchant has {len(recent_failures)} recent failures with other issues"
            should_escalate_early = True
            memory_evidence = recent_failures[-2:]
    
    # Priority 3: Same cause, different merchant
    elif cause_matches:
        successes = [a for a in cause_matches if a["outcome"] == "success"]
        if len(successes) >= 3:
            # This cause has been successfully resolved before - slight boost
            adjustment = 0.1
            reason = f"This cause successfully resolved {len(successes)} times for other merchants"
            memory_evidence = successes[-2:]
    
    # Calculate adjusted confidence
    adjusted_confidence = max(0.0, min(1.0, base_confidence + adjustment))
    
    return {
        "adjusted_confidence": adjusted_confidence,
        "adjustment": adjustment,
        "reason": reason,
        "should_escalate_early": should_escalate_early,
        "memory_evidence": memory_evidence
    }


def record_action(merchant_id: str, cause: str, action: str, outcome: str, 
                  confidence_before: float, confidence_after: float):
    """
    Records an action outcome to memory for future learning.
    
    Args:
        merchant_id: Merchant ID
        cause: Root cause
        action: Action taken
        outcome: "success" or "failure"
        confidence_before: Confidence before calibration
        confidence_after: Confidence after calibration
    """
    
    memory = load_memory()
    
    memory["actions"].append({
        "timestamp": datetime.now().isoformat(),
        "merchant_id": merchant_id,
        "cause": cause,
        "action": action,
        "outcome": outcome,
        "confidence_before": confidence_before,
        "confidence_after": confidence_after
    })
    
    save_memory(memory)
