"""
Test script for audio processing utilities.

This script verifies that the audio_processing utilities correctly
decode, detect, and normalize audio data from various sources.
"""

import base64
import sys
import os
from pathlib import Path

# Fix the Python path for imports
# The issue is that the 'src' directory is not properly recognized as a package
# We need to add the parent directory of 'src' to the path

# Get the absolute path to the audio_processing module
MODULE_DIR = os.path.abspath(os.path.join(
    os.path.dirname(__file__), 
    "src", "ai_interviewer", "utils"
))

# Add the module's directory to the Python path
if MODULE_DIR not in sys.path:
    sys.path.insert(0, MODULE_DIR)

# Now we can import directly from the file
try:
    from audio_processing import (
        detect_audio_format,
        decode_audio_data,
        normalize_audio,
        process_audio_data
    )
    print("Successfully imported audio processing functions!")
except ImportError as e:
    print(f"Import error: {e}")
    sys.exit(1)


def test_raw_bytes():
    """Test handling of raw audio bytes."""
    # Create a simple WAV header for testing
    # RIFF header (44 bytes for standard WAV)
    wav_header = (
        b'RIFF' +                  # ChunkID
        b'\x24\x00\x00\x00' +      # ChunkSize (36 + SubChunk2Size)
        b'WAVE' +                  # Format
        b'fmt ' +                  # Subchunk1ID
        b'\x10\x00\x00\x00' +      # Subchunk1Size (16 for PCM)
        b'\x01\x00' +              # AudioFormat (1 for PCM)
        b'\x01\x00' +              # NumChannels (1 for mono)
        b'\x44\xAC\x00\x00' +      # SampleRate (44100)
        b'\x88\x58\x01\x00' +      # ByteRate (SampleRate * NumChannels * BitsPerSample/8)
        b'\x02\x00' +              # BlockAlign (NumChannels * BitsPerSample/8)
        b'\x10\x00' +              # BitsPerSample (16 bits)
        b'data' +                  # Subchunk2ID
        b'\x00\x00\x00\x00'        # Subchunk2Size (0 for empty audio data)
    )
    
    # Test data
    test_bytes = wav_header + b'\x00\x00\x00\x00\x00\x00'  # Add some sample audio data
    
    print("== Testing with raw bytes ==")
    format_detected = detect_audio_format(test_bytes)
    print(f"Detected format: {format_detected}")
    
    decoded_bytes, decoded_format = decode_audio_data(test_bytes)
    print(f"Decoded format: {decoded_format}")
    print(f"Input size: {len(test_bytes)}, Output size: {len(decoded_bytes)}")
    
    normalized_bytes = normalize_audio(test_bytes, format_detected)
    print(f"Normalized audio size: {len(normalized_bytes)}")
    
    processed_bytes, metadata = process_audio_data(test_bytes)
    print(f"Processing metadata: {metadata}")
    
    assert format_detected == "wav", "Format detection failed"
    assert decoded_format == "wav", "Decoding failed"
    assert len(processed_bytes) > 0, "Processing failed"
    
    print("Raw bytes test passed!")


def test_base64_encoded():
    """Test handling of base64-encoded audio data."""
    # Create a simple WAV header and encode it as base64
    wav_header = (
        b'RIFF' +                  # ChunkID
        b'\x24\x00\x00\x00' +      # ChunkSize (36 + SubChunk2Size)
        b'WAVE' +                  # Format
        b'fmt ' +                  # Subchunk1ID
        b'\x10\x00\x00\x00' +      # Subchunk1Size (16 for PCM)
        b'\x01\x00' +              # AudioFormat (1 for PCM)
        b'\x01\x00' +              # NumChannels (1 for mono)
        b'\x44\xAC\x00\x00' +      # SampleRate (44100)
        b'\x88\x58\x01\x00' +      # ByteRate (SampleRate * NumChannels * BitsPerSample/8)
        b'\x02\x00' +              # BlockAlign (NumChannels * BitsPerSample/8)
        b'\x10\x00' +              # BitsPerSample (16 bits)
        b'data' +                  # Subchunk2ID
        b'\x00\x00\x00\x00'        # Subchunk2Size (0 for empty audio data)
    )
    
    # Test data with sample audio
    test_bytes = wav_header + b'\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09'
    base64_data = base64.b64encode(test_bytes).decode('ascii')
    
    print("\n== Testing with base64-encoded data ==")
    print(f"Base64 string length: {len(base64_data)}")
    
    decoded_bytes, decoded_format = decode_audio_data(base64_data)
    print(f"Decoded format: {decoded_format}")
    print(f"Original bytes size: {len(test_bytes)}, Decoded size: {len(decoded_bytes)}")
    
    processed_bytes, metadata = process_audio_data(base64_data)
    print(f"Processing metadata: {metadata}")
    
    assert decoded_format == "wav", "Format detection after base64 decoding failed"
    assert len(decoded_bytes) == len(test_bytes), "Base64 decoding size mismatch"
    assert len(processed_bytes) > 0, "Processing base64 data failed"
    
    print("Base64 encoded test passed!")


def main():
    """Run the audio processing tests."""
    print("Testing audio processing utilities...")
    
    test_raw_bytes()
    test_base64_encoded()
    
    print("\nAll audio processing tests passed! 🎉")


if __name__ == "__main__":
    main()
