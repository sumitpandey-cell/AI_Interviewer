"""
Test script to verify Google Cloud TTS integration works.
"""

import asyncio
import base64
import os
from pathlib import Path

# Set path to include the project
project_root = Path(__file__).resolve().parent
import sys
sys.path.append(str(project_root))

from src.ai_interviewer.utilities.tts_service import get_tts_service
from src.ai_interviewer.ai.workflow import interview_workflow
from src.ai_interviewer.interviews.schemas import LangGraphState

async def test_tts_integration():
    """Test TTS integration in the workflow."""
    
    print("Testing Google Cloud TTS integration...")
    
    # Get TTS service 
    tts_service = get_tts_service()
    if not tts_service:
        print("❌ TTS service not available. Check Google Cloud credentials.")
        return False
    
    # Test direct TTS conversion
    try:
        print("\nTesting direct TTS conversion...")
        audio_data = tts_service.synthesize_speech("Hello, this is a test of the Google Cloud Text-to-Speech integration.")
        if audio_data and 'audio' in audio_data and audio_data['audio']:
            print(f"✅ TTS conversion successful! Generated audio data length: {len(audio_data['audio'])}")
            
            # Save to file for manual verification
            audio_bytes = base64.b64decode(audio_data['audio'])
            with open("test_tts_output.wav", "wb") as f:
                f.write(audio_bytes)
            print(f"✅ Saved test audio to: {os.path.abspath('test_tts_output.wav')}")
        else:
            print("❌ TTS conversion failed - no audio data returned")
            return False
    except Exception as e:
        print(f"❌ Error in direct TTS test: {e}")
        return False
    
    # Test workflow integration
    try:
        print("\nTesting TTS in workflow...")
        
        # Create a test state
        state = LangGraphState(
            interview_id=1,
            session_token="test_session",
            current_step="initialize_session",
            user_id=1,
            interview_type="technical",
            position="Software Developer",
            questions_generated=[
                {"question": "Tell me about your experience with Python programming?", "type": "technical"}
            ],
            current_question_index=0
        )
        
        # Run present_question to trigger TTS generation
        updated_state = await interview_workflow.present_question(state)
        
        if hasattr(updated_state, 'audio_response') and updated_state.audio_response:
            print(f"✅ Workflow TTS integration successful! Generated audio data in workflow.")
            return True
        else:
            print("❌ Workflow TTS integration failed - no audio_response in state")
            return False
            
    except Exception as e:
        print(f"❌ Error in workflow TTS test: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(test_tts_integration())
