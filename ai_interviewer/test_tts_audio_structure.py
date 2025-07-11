#!/usr/bin/env python3
"""
Test script to verify the Google Cloud TTS integration audio format and structure.
This script tests that the TTS service generates the expected audio format for the frontend.
"""

import os
import sys
import json
import base64
from pathlib import Path

# Add src directory to path to allow importing the module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "src")))

# Import the TTS service
from ai_interviewer.utilities.tts_service import get_tts_service
from ai_interviewer.utilities.text_to_speech import TextToSpeech

def test_audio_structure():
    """Test audio structure for consistency with frontend expectations."""
    print("\n🔍 Testing Audio Structure Consistency...")
    
    # Get the TTS service
    tts_service = get_tts_service()
    
    if tts_service is None:
        print("❌ TTS service not available")
        return False
    
    # Test phrases
    test_phrases = [
        "Welcome to the interview. Let's start with a simple question.",
        "Tell me about your experience with Python development."
    ]
    
    for i, text in enumerate(test_phrases):
        print(f"\nTesting phrase #{i+1}: '{text[:30]}...'")
        
        try:
            # Generate audio
            audio_result = tts_service.synthesize_speech(text)
            
            # Verify structure
            if not audio_result:
                print(f"❌ Empty result returned")
                continue
                
            print(f"✓ Result is not None")
            
            if not isinstance(audio_result, dict):
                print(f"❌ Result is not a dict: {type(audio_result)}")
                continue
                
            print(f"✓ Result is a dict")
            
            if 'audio' not in audio_result:
                print(f"❌ 'audio' key missing from result: {list(audio_result.keys())}")
                continue
                
            print(f"✓ Result has 'audio' key")
            
            audio_data = audio_result['audio']
            if not audio_data:
                print(f"❌ 'audio' value is empty")
                continue
                
            audio_len = len(audio_data) if audio_data else 0
            print(f"✓ Audio data length: {audio_len} bytes")
            
            # Verify base64 encoding
            try:
                decoded_audio = base64.b64decode(audio_data)
                print(f"✓ Successfully decoded base64 data ({len(decoded_audio)} bytes)")
                
                # Write audio to file for manual testing
                output_dir = Path(__file__).parent / "tmp"
                output_dir.mkdir(exist_ok=True)
                output_file = output_dir / f"test_tts_{i+1}.wav"
                
                with open(output_file, "wb") as f:
                    f.write(decoded_audio)
                    
                print(f"✓ Saved decoded audio to {output_file}")
                
            except Exception as e:
                print(f"❌ Failed to decode base64 audio: {e}")
                continue
            
            # Save JSON representation for testing frontend compatibility
            json_file = output_dir / f"test_tts_{i+1}.json"
            with open(json_file, "w") as f:
                json.dump(audio_result, f)
                
            print(f"✓ Saved JSON representation to {json_file}")
                
        except Exception as e:
            print(f"❌ Test failed: {e}")
            continue
    
    return True

if __name__ == "__main__":
    print("🎤 Google Cloud TTS Audio Structure Test")
    print("=" * 60)
    
    success = test_audio_structure()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ Audio structure test completed. Check the output for details.")
        sys.exit(0)
    else:
        print("❌ Audio structure test failed. See errors above.")
        sys.exit(1)
