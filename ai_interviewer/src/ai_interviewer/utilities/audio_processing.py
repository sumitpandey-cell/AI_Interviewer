"""
Audio processing utilities for the AI Interviewer system.
Handles base64 encoded audio from various sources and prepares it for speech recognition.
"""

import base64
import io
from typing import Optional, Tuple, Dict, Any, Union

# Optional dependencies - we'll handle their absence gracefully
try:
    from pydub import AudioSegment
    PYDUB_AVAILABLE = True
except ImportError:
    PYDUB_AVAILABLE = False

try:
    import wave
    WAVE_AVAILABLE = True
except ImportError:
    WAVE_AVAILABLE = False


def detect_audio_format(audio_bytes: bytes) -> str:
    """
    Detect the audio format from binary data by examining signatures.
    
    Args:
        audio_bytes: Raw binary audio data
        
    Returns:
        String identifying the format ("wav", "webm", "mp3", "ogg", or "unknown")
    """
    if len(audio_bytes) < 12:
        return "unknown"  # Not enough data to detect format
        
    # Check for common audio format signatures
    if audio_bytes[:4] == b'RIFF' and audio_bytes[8:12] == b'WAVE':
        return "wav"
    elif b'webm' in audio_bytes[:50]:  # Check for webm signature in first 50 bytes
        return "webm"
    elif audio_bytes[:3] == b'ID3' or audio_bytes[:2] == b'\xff\xfb':
        return "mp3"
    elif audio_bytes[:4] == b'OggS':
        return "ogg"
    
    return "unknown"


def decode_audio_data(audio_data: Union[bytes, str]) -> Tuple[bytes, str]:
    """
    Decode audio data that could be either raw bytes or base64-encoded string.
    
    Args:
        audio_data: Either raw bytes or base64-encoded string
        
    Returns:
        Tuple of (decoded_bytes, detected_format)
    """
    # If it's already bytes, just detect format
    if isinstance(audio_data, bytes):
        return audio_data, detect_audio_format(audio_data)
    
    # If it's a string, assume base64 and decode
    try:
        audio_bytes = base64.b64decode(audio_data)
        detected_format = detect_audio_format(audio_bytes)
        return audio_bytes, detected_format
    except Exception as e:
        # If base64 decoding fails, raise an informative error
        raise ValueError(f"Failed to decode audio data: {e}")


def normalize_audio(audio_bytes: bytes, format_hint: str = "wav") -> bytes:
    """
    Normalize audio to 16kHz, mono, 16-bit format required by most speech APIs.
    
    Args:
        audio_bytes: Raw audio binary data
        format_hint: Format hint to help with conversion
    
    Returns:
        Normalized audio bytes in WAV format
    """
    if not PYDUB_AVAILABLE:
        # If pydub is not available, return original bytes
        return audio_bytes
    
    try:
        audio_io = io.BytesIO(audio_bytes)
        
        # Try to load with the detected format
        try:
            audio_segment = AudioSegment.from_file(audio_io, format=format_hint)
        except Exception:
            # If that fails, try without format specification
            audio_io.seek(0)
            audio_segment = AudioSegment.from_file(audio_io)
        
        # Convert to 16kHz, mono, 16-bit
        audio_segment = audio_segment.set_frame_rate(16000)
        audio_segment = audio_segment.set_channels(1)
        audio_segment = audio_segment.set_sample_width(2)  # 16-bit
        
        # Export to WAV format
        if WAVE_AVAILABLE:
            # Create WAV file manually for more control
            wav_io = io.BytesIO()
            with wave.open(wav_io, 'wb') as wav_file:
                wav_file.setnchannels(1)
                wav_file.setsampwidth(2)
                wav_file.setframerate(16000)
                wav_file.writeframes(audio_segment.raw_data)
            
            return wav_io.getvalue()
        else:
            # Fall back to pydub's export
            out_io = io.BytesIO()
            audio_segment.export(out_io, format="wav")
            return out_io.getvalue()
            
    except Exception as e:
        # If conversion fails, return original bytes
        print(f"Audio normalization failed: {e}, using original audio")
        return audio_bytes


def process_audio_data(audio_data: Union[bytes, str]) -> Tuple[bytes, Dict[str, Any]]:
    """
    Process audio data (raw bytes or base64) into a standardized format for speech recognition.
    
    Args:
        audio_data: Raw bytes or base64-encoded string containing audio data
    
    Returns:
        Tuple of (processed_audio_bytes, metadata)
    """
    # Step 1: Decode if necessary and detect format
    try:
        audio_bytes, detected_format = decode_audio_data(audio_data)
    except Exception as e:
        raise ValueError(f"Audio decoding failed: {e}")
    
    # Step 2: Normalize audio (if possible)
    try:
        processed_audio = normalize_audio(audio_bytes, detected_format)
    except Exception as e:
        print(f"Audio normalization failed: {e}, using original audio")
        processed_audio = audio_bytes
    
    # Step 3: Prepare metadata
    metadata = {
        "original_size": len(audio_bytes),
        "processed_size": len(processed_audio),
        "detected_format": detected_format,
        "processing_success": len(processed_audio) > 0
    }
    
    return processed_audio, metadata
