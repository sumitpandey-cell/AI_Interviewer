import os
from pathlib import Path
from .speech_to_text import SpeechToText

"""Speech to text service singleton for consistent access across the application."""


# Get the absolute path to the Google STT credentials file
base_dir = Path(__file__).resolve().parents[4]  # Go up 4 levels to the project root
stt_credentials_path = os.path.join(base_dir, "google_STT.json")

# Create a singleton instance of SpeechToText
stt_service = None

def get_stt_service():
    """Get or initialize the Speech-to-Text service."""
    global stt_service

    if stt_service is None:
        # Only initialize if the credentials file exists
        if os.path.exists(stt_credentials_path):
            try:
                stt_service = SpeechToText(stt_credentials_path)
                print(f"✅ STT Service initialized with credentials at {stt_credentials_path}")
            except Exception as e:
                print(f"⚠️ Failed to initialize STT service: {e}")
                return None
        else:
            print(f"⚠️ STT credentials file not found at {stt_credentials_path}")
            return None

    return stt_service