"""
Minimal test for audio format detection and base64 decoding.
"""
import os
import base64
import io
import wave

def detect_audio_format(audio_bytes):
    """Detect the audio format from binary data."""
    if len(audio_bytes) < 12:
        return "unknown"
        
    if audio_bytes[:4] == b'RIFF' and audio_bytes[8:12] == b'WAVE':
        return "wav"
    elif b'webm' in audio_bytes[:50]:
        return "webm"
    elif audio_bytes[:3] == b'ID3' or audio_bytes[:2] == b'\xff\xfb':
        return "mp3"
    elif audio_bytes[:4] == b'OggS':
        return "ogg"
    
    return "unknown"

def decode_base64_audio(base64_data):
    """Decode base64 audio data."""
    try:
        audio_bytes = base64.b64decode(base64_data)
        return audio_bytes, detect_audio_format(audio_bytes)
    except Exception as e:
        print(f"Error decoding base64: {e}")
        return None, "error"

# Create a simple WAV header for testing
def create_test_wav():
    """Create a test WAV file in memory."""
    wav_io = io.BytesIO()
    with wave.open(wav_io, 'wb') as wav_file:
        wav_file.setnchannels(1)  # mono
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(16000)  # 16kHz
        wav_file.writeframes(b'\x00\x01' * 1000)  # 1000 samples of audio
    
    return wav_io.getvalue()

# Test with raw bytes
test_wav = create_test_wav()
wav_format = detect_audio_format(test_wav)
print(f"WAV detection: {wav_format}")
assert wav_format == "wav", "WAV detection failed"

# Test with base64 encoding
base64_wav = base64.b64encode(test_wav).decode('ascii')
print(f"Base64 WAV length: {len(base64_wav)}")

decoded_bytes, decoded_format = decode_base64_audio(base64_wav)
print(f"Decoded format: {decoded_format}")
print(f"Original bytes length: {len(test_wav)}, Decoded bytes length: {len(decoded_bytes)}")
assert decoded_format == "wav", "Base64 WAV detection failed"
assert len(decoded_bytes) == len(test_wav), "Base64 decoding size mismatch"

print("All tests passed! 🎉")
