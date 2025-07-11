#!/usr/bin/env python3
"""
Test script to verify the Google Cloud TTS integration.
This script tests that the TTS service can properly generate base64-encoded audio.
"""

import os
import sys
import base64
import json
from google.cloud import texttospeech
from google.oauth2 import service_account

# Add src directory to path to allow importing the module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "src")))

# Import the TTS service
from ai_interviewer.utilities.tts_service import get_tts_service
from ai_interviewer.utilities.text_to_speech import GoogleTextToSpeech

def verify_credentials():
    """Verify that the Google Cloud credentials file exists and is valid."""
    creds_file = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS") or "google_TTS.json"
    
    if not os.path.exists(creds_file):
        print(f"❌ Credentials file not found: {creds_file}")
        print("Please ensure the Google Cloud credentials file exists.")
        return False
    
    try:
        # Try to load the credentials
        credentials = service_account.Credentials.from_service_account_file(creds_file)
        
        # Print info about the credentials
        with open(creds_file, 'r') as f:
            creds_data = json.load(f)
        
        print(f"✅ Credentials loaded successfully")
        print(f"Project ID: {creds_data.get('project_id', 'N/A')}")
        print(f"Client Email: {creds_data.get('client_email', 'N/A')}")
        return True
    except Exception as e:
        print(f"❌ Failed to load credentials: {e}")
        return False

def test_tts_service():
    """Test the TTS service singleton."""
    print("\n🔍 Testing TTS Service Singleton...")
    
    # Get the TTS service
    tts_service = get_tts_service()
    
    if tts_service is None:
        print("❌ TTS service not available")
        return False
    
    print(f"✅ TTS service loaded: {type(tts_service).__name__}")
    return True

def test_speech_synthesis():
    """Test synthesizing speech with different text samples."""
    print("\n🔍 Testing Speech Synthesis...")
    
    # Get the TTS service
    tts_service = get_tts_service()
    
    if tts_service is None:
        print("❌ TTS service not available")
        return False
    
    test_texts = [
        "Hello, this is a test of the Google Cloud Text-to-Speech integration.",
        "Tell me about your experience with Python programming.",
        "What would you do if a critical system went down during a major release?",
        "How do you handle disagreements with team members?"
    ]
    
    for i, text in enumerate(test_texts):
        print(f"\nSynthesizing text #{i+1}: '{text[:30]}...'")
        
        try:
            audio_base64 = tts_service.synthesize_speech(
                text,
                language_code="en-US",
                voice_name="en-US-Studio-O",
                speaking_rate=0.95
            )
            
            # Check if we got valid base64 data
            if not audio_base64:
                print(f"❌ No audio data returned for text #{i+1}")
                continue
            
            # Decode a small portion to verify it's valid base64
            try:
                decoded = base64.b64decode(audio_base64[:100])
                print(f"✅ Successfully synthesized audio for text #{i+1}")
                print(f"   Audio length: {len(audio_base64)} base64 chars")
            except Exception as e:
                print(f"❌ Invalid base64 data: {e}")
                continue
                
        except Exception as e:
            print(f"❌ Failed to synthesize speech: {e}")
    
    return True

def test_direct_client():
    """Test creating a direct client to the Google Cloud TTS API."""
    print("\n🔍 Testing Direct Client Connection...")
    
    try:
        # Create the client directly
        client = texttospeech.TextToSpeechClient()
        
        # Try a simple synthesis
        synthesis_input = texttospeech.SynthesisInput(text="This is a direct client test.")
        
        voice = texttospeech.VoiceSelectionParams(
            language_code="en-US",
            name="en-US-Standard-D"
        )
        
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.LINEAR16,
            speaking_rate=1.0,
            pitch=0.0
        )
        
        response = client.synthesize_speech(
            input=synthesis_input,
            voice=voice,
            audio_config=audio_config
        )
        
        print(f"✅ Direct client connection successful")
        print(f"   Audio length: {len(response.audio_content)} bytes")
        
        return True
    except Exception as e:
        print(f"❌ Direct client connection failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🎤 Google Cloud Text-to-Speech Integration Test")
    print("=" * 60)
    
    # Test each component
    creds_ok = verify_credentials()
    service_ok = test_tts_service()
    synthesis_ok = test_speech_synthesis()
    client_ok = test_direct_client()
    
    # Overall results
    print("\n" + "=" * 60)
    print("📊 Test Results:")
    print(f"Credentials Verification: {'✅ PASS' if creds_ok else '❌ FAIL'}")
    print(f"TTS Service Singleton: {'✅ PASS' if service_ok else '❌ FAIL'}")
    print(f"Speech Synthesis: {'✅ PASS' if synthesis_ok else '❌ FAIL'}")
    print(f"Direct Client Connection: {'✅ PASS' if client_ok else '❌ FAIL'}")
    
    if all([creds_ok, service_ok, synthesis_ok, client_ok]):
        print("\n✅ All tests passed! Google Cloud TTS integration is working properly.")
        return 0
    else:
        print("\n❌ Some tests failed. Please check the logs above for details.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
