import base64
import io
from typing import Optional
from pydub import AudioSegment
from google.cloud import speech
import os

class SpeechToText:
    def __init__(self, credentials_path, language_code="en-US"):
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path
        self.client = speech.SpeechClient()
        self.config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=16000,
            language_code=language_code,
            audio_channel_count=1,
        )

    def convert_base64_to_text(self, audio_base64: str, input_format: Optional[str] = "webm"):
        try:
            # Ensure audio_base64 is a string
            if not isinstance(audio_base64, str):
                raise TypeError(f"Expected audio_base64 to be str, got {type(audio_base64)}")

            # Remove data URL prefix if present (e.g., "data:audio/wav;base64,")
            if audio_base64.startswith("data:"):
                audio_base64 = audio_base64.split(",")[1]
                print(f"Removed data URL prefix from base64 string")

            # Fix missing base64 padding
            missing_padding = len(audio_base64) % 4
            if missing_padding:
                audio_base64 = audio_base64 + '=' * (4 - missing_padding)
                print(f"Added {4 - missing_padding} padding characters")

            # Decode base64 to bytes
            try:
                audio_bytes = base64.b64decode(audio_base64)
            except Exception as e:
                raise ValueError(f"Base64 decoding failed: {str(e)}")

            if not audio_bytes:
                raise ValueError("Empty audio data after base64 decoding")
            print(f"Decoded audio bytes: {len(audio_bytes)} bytes")

            # Save raw input for debugging
            debug_extension = "wav" if input_format == "wav" else input_format
            with open(f"debug_input_audio.{debug_extension}", "wb") as f:
                f.write(audio_bytes)

            # Validate audio format
            if input_format == "wav":
                if not audio_bytes.startswith(b'RIFF'):
                    raise ValueError("Invalid WAV audio data: Missing RIFF header")
            elif input_format == "webm":
                if not audio_bytes.startswith(b'\x1A\x45\xDF\xA3'):
                    raise ValueError("Invalid WebM audio data: Missing EBML header")

            # Decode audio with pydub
            try:
                audio_segment = AudioSegment.from_file(io.BytesIO(audio_bytes), format=input_format)
            except Exception as e:
                raise RuntimeError(f"Failed to decode audio ({input_format}): {str(e)}")

            print(f"Original audio: {audio_segment.frame_rate}Hz, {audio_segment.channels}ch, {audio_segment.sample_width*8}-bit")

            # Convert to 16kHz, mono, 16-bit WAV
            audio_segment = audio_segment.set_frame_rate(16000).set_channels(1).set_sample_width(2)

            # Export to WAV bytes
            wav_io = io.BytesIO()
            audio_segment.export(wav_io, format="wav")
            wav_bytes = wav_io.getvalue()
            print(f"Converted WAV size: {len(wav_bytes)} bytes")

            # Save converted WAV for debugging
            with open("debug_output_audio.wav", "wb") as f:
                f.write(wav_bytes)

            # Send to Google STT
            audio = speech.RecognitionAudio(content=wav_bytes)
            return self.speech_to_text(self.config, audio)

        except Exception as e:
            raise RuntimeError(f"Error processing audio: {str(e)}")

    def speech_to_text(self, config, audio):
        response = self.client.recognize(config=config, audio=audio)
        print("STT response received:", response)
        return response

    def get_transcript(self, response):
        return " ".join(result.alternatives[0].transcript for result in response.results if result.alternatives)