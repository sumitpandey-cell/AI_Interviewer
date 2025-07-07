#!/usr/bin/env python3
"""
Test script to verify the datetime serialization fix
"""

import json
from datetime import datetime
from typing import Dict, Any

def clean_workflow_state_for_db(workflow_state: Dict[str, Any]) -> Dict[str, Any]:
    """Clean workflow state by converting datetime objects to strings for JSON serialization."""
    
    def clean_value(value):
        if isinstance(value, datetime):
            return value.isoformat()
        elif isinstance(value, dict):
            return {k: clean_value(v) for k, v in value.items()}
        elif isinstance(value, list):
            return [clean_value(item) for item in value]
        else:
            return value
    
    cleaned = clean_value(workflow_state)
    # Ensure we always return a dict
    return cleaned if isinstance(cleaned, dict) else {}

def test_datetime_serialization():
    """Test that datetime objects are properly serialized."""
    
    # Create a sample workflow state with datetime objects
    sample_state = {
        "interview_id": 1,
        "session_token": "test-token",
        "current_step": "present_question",
        "user_id": 5,
        "created_at": datetime.now(),
        "responses_history": [
            {
                "timestamp": datetime.now(),
                "response": "Sample response",
                "evaluation": {
                    "score": 8.5,
                    "created_at": datetime.now()
                }
            }
        ],
        "metadata": {
            "start_time": datetime.now(),
            "nested_data": {
                "last_update": datetime.now(),
                "scores": [7, 8, 9]
            }
        }
    }
    
    print("Original state (with datetime objects):")
    print(f"Type of created_at: {type(sample_state['created_at'])}")
    print(f"Value: {sample_state['created_at']}")
    
    # Clean the state
    cleaned_state = clean_workflow_state_for_db(sample_state)
    
    print("\nCleaned state (datetime converted to strings):")
    print(f"Type of created_at: {type(cleaned_state['created_at'])}")
    print(f"Value: {cleaned_state['created_at']}")
    
    # Test JSON serialization
    try:
        json_str = json.dumps(cleaned_state)
        print("\n✅ JSON serialization successful!")
        print(f"JSON string length: {len(json_str)} characters")
        
        # Test deserialization
        restored_state = json.loads(json_str)
        print("✅ JSON deserialization successful!")
        
        return True
        
    except Exception as e:
        print(f"\n❌ JSON serialization failed: {e}")
        return False

if __name__ == "__main__":
    print("Testing datetime serialization fix...")
    success = test_datetime_serialization()
    
    if success:
        print("\n🎉 All tests passed! The datetime serialization fix is working correctly.")
    else:
        print("\n💥 Tests failed. The fix needs more work.")
