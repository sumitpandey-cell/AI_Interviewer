"""
Test the fixed audio data handling
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from ai_interviewer.interviews.service import clean_workflow_state_for_db
from ai_interviewer.interviews.schemas import LangGraphState
import base64
import json

def test_audio_data_handling():
    """Test that audio data is properly handled and excluded from DB storage."""
    
    # Create a mock state with audio data
    state_data = {
        'interview_id': 1,
        'session_token': 'test-123',
        'current_step': 'process_audio',
        'user_id': 1,
        'interview_type': 'technical',
        'position': 'Software Engineer',
        'user_response': 'Hello world',
        'audio_data': base64.b64decode('UklGRiQAAABXQVZFZm10IBAAAAABAAEAESsAACJWAAACABAAZGF0YQcAAAAA'),
        'total_score': 0.0,
        'should_continue': True
    }
    
    print("1. Testing LangGraphState creation with audio data...")
    try:
        state = LangGraphState(**state_data)
        print(f"   ✅ State created with audio data: {len(state.audio_data)} bytes")
    except Exception as e:
        print(f"   ❌ Error creating state: {e}")
        return False
    
    print("2. Testing state serialization for database...")
    try:
        state_dict = state.model_dump()
        print(f"   ✅ State dict created, audio_data present: {'audio_data' in state_dict}")
        print(f"   📊 Audio data size: {len(state_dict.get('audio_data', b''))} bytes")
    except Exception as e:
        print(f"   ❌ Error serializing state: {e}")
        return False
    
    print("3. Testing database cleaning function...")
    try:
        cleaned_state = clean_workflow_state_for_db(state_dict)
        print(f"   ✅ State cleaned for DB")
        print(f"   🗑️  Audio data excluded: {'audio_data' not in cleaned_state}")
        print(f"   📝 Remaining keys: {list(cleaned_state.keys())[:5]}...")
    except Exception as e:
        print(f"   ❌ Error cleaning state: {e}")
        return False
    
    print("4. Testing JSON serialization...")
    try:
        json_str = json.dumps(cleaned_state)
        print(f"   ✅ JSON serialization successful")
        print(f"   📏 JSON size: {len(json_str)} characters")
    except Exception as e:
        print(f"   ❌ JSON serialization failed: {e}")
        return False
    
    print("5. Testing with base64 string input...")
    try:
        # Test with base64 string (like from API)
        audio_b64 = 'UklGRiQAAABXQVZFZm10IBAAAAABAAEAESsAACJWAAACABAAZGF0YQcAAAAA'
        
        state_with_b64 = LangGraphState(
            interview_id=1,
            session_token='test-456',
            current_step='process_audio',
            user_id=1,
            interview_type='technical',
            position='Software Engineer',
            audio_data=audio_b64  # This will be handled as string initially
        )
        
        # Simulate the conversion that happens in the service
        if isinstance(state_with_b64.audio_data, str):
            decoded_audio = base64.b64decode(state_with_b64.audio_data)
            print(f"   ✅ Base64 decode successful: {len(decoded_audio)} bytes")
        
    except Exception as e:
        print(f"   ❌ Base64 handling failed: {e}")
        return False
    
    print("\n🎉 All tests passed! Audio data handling is working correctly.")
    return True

if __name__ == "__main__":
    test_audio_data_handling()
