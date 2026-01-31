import os
import json
from typing import Dict, List, Optional

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

def reason(ticket: Dict, logs: List[Dict], rules_text: str) -> Optional[Dict]:
    """
    LLM-powered reasoning that generates multiple hypotheses and selects the most likely root cause.
    
    Args:
        ticket: Dictionary with merchant_id, subject, message
        logs: List of log entries for this merchant
        rules_text: Migration guide rules
    
    Returns:
        Dictionary with:
        - hypotheses: List of possible causes
        - selected_cause: Most likely root cause
        - confidence: 0-1 confidence score
        - reasoning_chain: Step-by-step logic
        - evidence_logs: Relevant log entries
        - evidence_docs: Matching rules from docs
    """
    
    if not GEMINI_AVAILABLE:
        return None
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return None
    
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Prepare context
        merchant_id = ticket["merchant_id"]
        issue = ticket["subject"]
        message = ticket["message"]
        
        logs_text = json.dumps(logs, indent=2)
        
        prompt = f"""You are an expert AI systems engineer diagnosing headless commerce migration issues.

MERCHANT: {merchant_id}
ISSUE: {issue}
DESCRIPTION: {message}

RELEVANT LOGS:
{logs_text}

MIGRATION RULES:
{rules_text}

Your task:
1. Generate 3-5 possible hypotheses for the root cause
2. Analyze evidence from logs and rules for each hypothesis
3. Select the most likely root cause
4. Assign a confidence score (0.0 to 1.0)
5. Explain your reasoning step-by-step

Respond in JSON format:
{{
  "hypotheses": [
    {{"cause": "description", "evidence": "what supports this"}},
    ...
  ],
  "selected_cause": "most likely root cause",
  "confidence": 0.0-1.0,
  "reasoning_chain": [
    "Step 1: ...",
    "Step 2: ...",
    ...
  ],
  "evidence_logs": ["relevant log messages"],
  "evidence_docs": ["relevant rule numbers or descriptions"]
}}

Be precise and evidence-based. Only high confidence (>0.8) if evidence is strong and clear."""

        response = model.generate_content(prompt)
        
        # Parse JSON response
        response_text = response.text.strip()
        
        # Remove markdown code blocks if present
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.startswith("```"):
            response_text = response_text[3:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
        
        result = json.loads(response_text.strip())
        
        # Validate structure
        required_keys = ["hypotheses", "selected_cause", "confidence", "reasoning_chain", "evidence_logs", "evidence_docs"]
        if not all(key in result for key in required_keys):
            return None
        
        # Ensure confidence is in valid range
        result["confidence"] = max(0.0, min(1.0, float(result["confidence"])))
        
        return result
        
    except Exception as e:
        print(f"LLM reasoning failed: {e}")
        return None
