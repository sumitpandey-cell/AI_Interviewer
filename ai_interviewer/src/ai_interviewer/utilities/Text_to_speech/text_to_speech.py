"""Synthesize text to speech base64 using Google Cloud Text-to-Speech API."""
import os
from google.cloud import texttospeech
import base64

class TextToSpeech:
    def __init__(self, credentials_path):
        """Initialize the Text-to-Speech client with Google credentials."""
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path
        self.client = texttospeech.TextToSpeechClient()

    def synthesize_speech(self, text,
                         language_code="en-US", voice_name="en-US-Studio-O",
                         speaking_rate=1.0):
        """Convert text to speech and return base64 encoded audio."""
        # Clean and prepare text for better synthesis
        try:
            text = text.strip()
            if not text:
                print("⚠️ Warning: Empty text provided for TTS")
                return {'audio': ''}
            
            # Create input text
            input_text = texttospeech.SynthesisInput(text=text)

            # Set voice parameters
            voice = texttospeech.VoiceSelectionParams(
                language_code=language_code,
                name=voice_name,
            )

            # Set audio configuration with optimized settings
            audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.LINEAR16,
                speaking_rate=speaking_rate,
                sample_rate_hertz=24000,  # Higher sample rate for better quality
                effects_profile_id=["telephony-class-application"]  # Better for speech
            )

            # Generate speech
            response = self.client.synthesize_speech(
                request={"input": input_text, "voice": voice, "audio_config": audio_config}
            )
            audio_base64 = base64.b64encode(response.audio_content).decode('utf-8')

            print(f"✅ Generated {len(audio_base64)} bytes of base64 audio")
            return {'audio': audio_base64}
        except Exception as e:
            print(f"⚠️ TTS conversion error: {str(e)}")
            # Return empty audio instead of None to keep consistent return type
            return {'audio': ''}
