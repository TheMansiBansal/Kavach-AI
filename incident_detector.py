from datetime import datetime, timedelta
from typing import List, Dict
from collections import defaultdict

def detect_patterns(logs: List[Dict], time_window_minutes: int = 10, threshold: int = 10) -> Dict:
    """
    Detects cross-merchant incident patterns.
    
    Args:
        logs: All log entries across all merchants
        time_window_minutes: Time window for pattern detection (default 10 min)
        threshold: Minimum number of merchants to trigger platform-wide alert (default 10)
    
    Returns:
        Dictionary with:
        - incident_type: "PLATFORM-WIDE" or "MERCHANT-SPECIFIC"
        - affected_merchants: List of merchant IDs
        - pattern: Description of the pattern
        - time_range: Start and end timestamps
        - should_block_auto_fix: Boolean
    """
    
    if not logs:
        return {
            "incident_type": "MERCHANT-SPECIFIC",
            "affected_merchants": [],
            "pattern": "No logs available",
            "time_range": None,
            "should_block_auto_fix": False
        }
    
    # Parse timestamps and group by error type and time window
    error_patterns = defaultdict(lambda: defaultdict(set))
    
    for log in logs:
        try:
            timestamp = datetime.fromisoformat(log["timestamp"].replace("Z", "+00:00"))
            error_code = log.get("error_code", 0)
            merchant_id = log.get("merchant_id", "unknown")
            message = log.get("message", "")
            
            # Group by error code
            time_bucket = timestamp.replace(second=0, microsecond=0)
            error_patterns[error_code][time_bucket].add(merchant_id)
            
        except Exception as e:
            continue
    
    # Check for platform-wide incidents
    platform_incidents = []
    
    for error_code, time_buckets in error_patterns.items():
        for time_bucket, merchants in time_buckets.items():
            # Check if enough merchants affected in this time window
            if len(merchants) >= threshold:
                # Check within the time window
                window_start = time_bucket
                window_end = time_bucket + timedelta(minutes=time_window_minutes)
                
                # Count unique merchants in this window
                merchants_in_window = set()
                for tb, merch_set in time_buckets.items():
                    if window_start <= tb <= window_end:
                        merchants_in_window.update(merch_set)
                
                if len(merchants_in_window) >= threshold:
                    platform_incidents.append({
                        "error_code": error_code,
                        "merchants": list(merchants_in_window),
                        "count": len(merchants_in_window),
                        "time_start": window_start.isoformat(),
                        "time_end": window_end.isoformat()
                    })
    
    # Return platform-wide incident if detected
    if platform_incidents:
        # Get the most severe incident (most merchants affected)
        worst_incident = max(platform_incidents, key=lambda x: x["count"])
        
        return {
            "incident_type": "PLATFORM-WIDE",
            "affected_merchants": worst_incident["merchants"],
            "pattern": f"{worst_incident['count']} merchants experiencing error {worst_incident['error_code']} within {time_window_minutes} minutes",
            "time_range": {
                "start": worst_incident["time_start"],
                "end": worst_incident["time_end"]
            },
            "should_block_auto_fix": True,
            "escalation_priority": "CRITICAL"
        }
    
    # Check for repeated errors across multiple merchants (lower threshold)
    error_counts = defaultdict(set)
    for error_code, time_buckets in error_patterns.items():
        for merchants in time_buckets.values():
            error_counts[error_code].update(merchants)
    
    for error_code, merchants in error_counts.items():
        if len(merchants) >= 5:  # 5+ merchants with same error (but not in same time window)
            return {
                "incident_type": "POTENTIAL-PLATFORM-ISSUE",
                "affected_merchants": list(merchants),
                "pattern": f"{len(merchants)} merchants experiencing error {error_code} (not time-clustered)",
                "time_range": None,
                "should_block_auto_fix": False,
                "escalation_priority": "HIGH"
            }
    
    # Default: merchant-specific
    return {
        "incident_type": "MERCHANT-SPECIFIC",
        "affected_merchants": [],
        "pattern": "Individual merchant issues",
        "time_range": None,
        "should_block_auto_fix": False,
        "escalation_priority": "NORMAL"
    }


def check_merchant_in_incident(merchant_id: str, incident_info: Dict) -> bool:
    """
    Checks if a specific merchant is part of a detected platform-wide incident.
    
    Args:
        merchant_id: Merchant to check
        incident_info: Result from detect_patterns()
    
    Returns:
        True if merchant is part of platform-wide incident
    """
    if incident_info["incident_type"] in ["PLATFORM-WIDE", "POTENTIAL-PLATFORM-ISSUE"]:
        return merchant_id in incident_info["affected_merchants"]
    return False
