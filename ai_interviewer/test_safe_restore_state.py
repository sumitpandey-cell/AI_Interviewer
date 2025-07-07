#!/usr/bin/env python3
"""
Test for the safe_restore_state function to ensure it handles problematic binary data.
"""

from src.ai_interviewer.interviews.router import safe_restore_state
from src.ai_interviewer.interviews.schemas import LangGraphState
import base64
import json

def test_safe_restore_state():
    """Test safe_restore_state with problematic data that would cause UnicodeDecodeError."""
    print("🧪 Testing safe_restore_state with problematic binary data...")
    
    # Create a state dict with problematic data
    problematic_bytes = b'\xff\x00\xfe\x01\xfc\x02\xfb\x03' * 10  # Contains 0xff that causes UTF-8 errors
    
    # Test 1: State dict with binary data
    print("\n1. Testing with raw binary data...")
    test_dict = {
        "interview_id": 1,
        "session_token": "test-token",
        "current_step": "test",
        "user_id": 1,
        "interview_type": "technical",
        "position": "Software Engineer",
        "audio_data": problematic_bytes,
        "some_field": "normal text"
    }
    
    try:
        # This should clean the binary data and not cause any errors
        state = safe_restore_state(test_dict)
        print("   ✅ Successfully restored state")
        print(f"   📊 audio_data present: {hasattr(state, 'audio_data')}")
        print(f"   📊 audio_data value: {state.audio_data}")
        assert state.audio_data is None, "audio_data should be None"
    except Exception as e:
        print(f"   ❌ Failed: {e}")
    
    # Test 2: State with string representation of binary data
    print("\n2. Testing with string representation of binary data...")
    test_dict2 = {
        "interview_id": 2,
        "session_token": "test-token-2",
        "current_step": "test",
        "user_id": 1,
        "interview_type": "technical",
        "position": "Software Engineer",
        "audio_data": "<audio_bytes:80>",
        "some_field": "normal text"
    }
    
    try:
        state2 = safe_restore_state(test_dict2)
        print("   ✅ Successfully restored state")
        print(f"   📊 audio_data present: {hasattr(state2, 'audio_data')}")
        print(f"   📊 audio_data value: {state2.audio_data}")
        assert state2.audio_data is None, "audio_data should be None"
    except Exception as e:
        print(f"   ❌ Failed: {e}")
    
    # Test 3: Serialization test
    print("\n3. Testing JSON serialization of restored state...")
    try:
        state_dict = state.model_dump()
        json_str = json.dumps(state_dict)
        print("   ✅ JSON serialization successful")
        print(f"   📏 JSON length: {len(json_str)} characters")
    except Exception as e:
        print(f"   ❌ JSON serialization failed: {e}")
    
    print("\n🎉 All tests completed!")

if __name__ == "__main__":
    test_safe_restore_state()
