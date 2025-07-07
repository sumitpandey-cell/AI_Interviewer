"""
Test script to verify the submit response API works with audio data
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src"))

import json
import base64
from ai_interviewer.interviews.service import clean_workflow_state_for_db
from ai_interviewer.interviews.schemas import LangGraphState

def test_your_specific_payload():
    """Test with the exact payload you're sending."""
    
    # Your exact payload
    payload = {
        "session_token": "f9277e57-964f-49f6-a55c-8de7b3793693",
        "response_text": "Hello",
        "audio_data": "UklGRiQAAABXQVZFZm10IBAAAAABAAEAESsAACJWAAACABAAZGF0YQcAAAAA//8AAP//AAD//wAA//8AAP//AAD//wAA//8AAP//AAD//wAA//8AAP//AAD//wAA//8AAP//AAD//wAA"
    }
    
    print("Testing your exact payload...")
    print(f"Session token: {payload['session_token']}")
    print(f"Response text: '{payload['response_text']}'")
    print(f"Audio data (base64): {payload['audio_data'][:50]}...")
    
    # Decode the audio data (this is what the service will do)
    try:
        audio_bytes = base64.b64decode(payload['audio_data'])
        print(f"✅ Audio decoded successfully: {len(audio_bytes)} bytes")
    except Exception as e:
        print(f"❌ Failed to decode audio: {e}")
        return
    
    # Create a mock state similar to what would happen in the service
    state_data = {
        'interview_id': 2,
        'session_token': payload['session_token'],
        'current_step': 'process_response',
        'user_id': 1,
        'interview_type': 'technical',
        'position': 'Software Engineer',
        'user_response': payload['response_text'],
        'audio_data': audio_bytes,  # Raw bytes
        'total_score': 0.0,
        'should_continue': True,
        'responses_history': [],
        'questions_generated': [{'question': 'Test question', 'type': 'technical'}]
    }
    
    print("\nTesting state creation and cleaning...")
    try:
        # Create the state
        state = LangGraphState(**state_data)
        print("✅ LangGraphState created successfully")
        
        # Convert to dict (this happens before DB save)
        state_dict = state.model_dump()
        print("✅ State serialized to dict")
        
        # Clean for database (this is where the error was happening)
        cleaned_state = clean_workflow_state_for_db(state_dict)
        print("✅ State cleaned for database")
        print(f"📝 Audio data excluded: {'audio_data' not in cleaned_state}")
        
        # Test JSON serialization (this is what SQLAlchemy does)
        json_str = json.dumps(cleaned_state)
        print("✅ JSON serialization successful")
        print(f"📏 Cleaned state size: {len(json_str)} characters")
        
        print("\n🎉 SUCCESS: Your payload should now work without the JSON error!")
        
    except Exception as e:
        print(f"❌ Error during processing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_your_specific_payload()
