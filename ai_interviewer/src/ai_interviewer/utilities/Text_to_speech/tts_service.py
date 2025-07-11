"""Text to speech service singleton for consistent access across the application."""

import os
from pathlib import Path
from .text_to_speech import TextToSpeech

# Get the absolute path to the Google TTS credentials file
base_dir = Path(__file__).resolve().parents[4]  # Go up 4 levels to the project root
tts_credentials_path = os.path.join(base_dir, "google_TTS.json")

# Create a singleton instance of TextToSpeech
tts_service = None

def get_tts_service():
    """Get or initialize the Text-to-Speech service."""
    global tts_service
    
    if tts_service is None:
        # Only initialize if the credentials file exists
        if os.path.exists(tts_credentials_path):
            try:
                tts_service = TextToSpeech(tts_credentials_path)
                print(f"✅ TTS Service initialized with credentials at {tts_credentials_path}")
            except Exception as e:
                print(f"⚠️ Failed to initialize TTS service: {e}")
                return None
        else:
            print(f"⚠️ TTS credentials file not found at {tts_credentials_path}")
            return None
            
    return tts_service
