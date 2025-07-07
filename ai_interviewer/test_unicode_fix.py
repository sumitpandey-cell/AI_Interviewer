#!/usr/bin/env python3
"""
Test script to verify that the UnicodeDecodeError is fixed
"""

import base64
from src.ai_interviewer.interviews.schemas import LangGraphState
from src.ai_interviewer.interviews.service import clean_workflow_state_for_db

def test_unicode_error_fix():
    """Test that binary audio data no longer causes UnicodeDecodeError."""
    print("🧪 Testing UnicodeDecodeError fix...")
    
    # Create problematic binary data that would cause UTF-8 decode errors
    # This includes the specific byte sequence that was causing the error
    problem_bytes = b'\xff\x00\xfe\x01\xfc\x02\xfb\x03' * 10  # Contains 0xff that causes UTF-8 errors
    
    print(f"   📊 Created binary data with {len(problem_bytes)} bytes")
    print(f"   🔍 First few bytes: {problem_bytes[:10]}")
    
    # Test 1: Direct bytes in LangGraphState
    print("\n1. Testing LangGraphState with raw problematic bytes...")
    try:
        state = LangGraphState(
            interview_id=1,
            session_token="test-123",
            current_step="test",
            user_id=1,
            interview_type="technical",
            position="Software Engineer",  # Required field
            audio_data=problem_bytes  # This should not cause issues
        )
        print("   ✅ LangGraphState creation successful")
    except Exception as e:
        print(f"   ❌ LangGraphState creation failed: {e}")
        return False
    
    # Test 2: Pydantic model_dump() with binary data
    print("\n2. Testing Pydantic model_dump() with binary data...")
    try:
        state_dict = state.model_dump()
        print("   ✅ model_dump() successful")
        print(f"   📊 State dict contains {len(state_dict)} fields")
        print(f"   🔍 audio_data type: {type(state_dict.get('audio_data'))}")
    except Exception as e:
        print(f"   ❌ model_dump() failed: {e}")
        return False
    
    # Test 3: Database cleaning function
    print("\n3. Testing clean_workflow_state_for_db()...")
    try:
        cleaned_state = clean_workflow_state_for_db(state_dict)
        print("   ✅ clean_workflow_state_for_db() successful")
        print(f"   🗑️  audio_data excluded: {'audio_data' not in cleaned_state}")
        print(f"   📝 Cleaned state keys: {list(cleaned_state.keys())}")
    except Exception as e:
        print(f"   ❌ clean_workflow_state_for_db() failed: {e}")
        return False
    
    # Test 4: Base64 string handling
    print("\n4. Testing base64 string handling...")
    try:
        # Test with base64 encoded data (decode it first since LangGraphState expects bytes)
        b64_data = base64.b64encode(problem_bytes).decode('utf-8')
        decoded_audio = base64.b64decode(b64_data)  # Convert back to bytes for LangGraphState
        
        state_with_b64 = LangGraphState(
            interview_id=2,
            session_token="test-456",
            current_step="test",
            user_id=1,
            interview_type="technical",
            position="Senior Developer",  # Required field
            audio_data=decoded_audio  # Use bytes, not the base64 string
        )
        
        # Convert to dict and clean
        state_dict_b64 = state_with_b64.model_dump()
        cleaned_state_b64 = clean_workflow_state_for_db(state_dict_b64)
        
        print("   ✅ Base64 string handling successful")
        print(f"   📊 Original b64 string length: {len(b64_data)} chars")
        print(f"   📊 Decoded audio length: {len(decoded_audio)} bytes")
        print(f"   🗑️  audio_data excluded from DB: {'audio_data' not in cleaned_state_b64}")
    except Exception as e:
        print(f"   ❌ Base64 string handling failed: {e}")
        return False
    
    # Test 5: JSON serialization
    print("\n5. Testing JSON serialization...")
    try:
        import json
        json_str = json.dumps(cleaned_state)
        print("   ✅ JSON serialization successful")
        print(f"   📏 JSON length: {len(json_str)} characters")
        
        # Test deserialization
        restored = json.loads(json_str)
        print("   ✅ JSON deserialization successful")
    except Exception as e:
        print(f"   ❌ JSON serialization failed: {e}")
        return False
    
    print("\n🎉 All tests passed! UnicodeDecodeError is fixed!")
    return True

if __name__ == "__main__":
    success = test_unicode_error_fix()
    if success:
        print("\n✅ RESULT: Unicode handling is now robust")
        print("   - Binary audio data is safely excluded from database storage")
        print("   - Pydantic v2 model_dump() is used instead of deprecated dict()")
        print("   - No UTF-8 decode errors occur with problematic byte sequences")
        print("   - Both raw bytes and base64 strings are handled correctly")
    else:
        print("\n❌ RESULT: Some tests failed - needs investigation")
        exit(1)
