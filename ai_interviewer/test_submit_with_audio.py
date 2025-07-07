"""
Test script for interview submit API - With mock audio data
"""
import requests
import json
import base64

# API base URL
BASE_URL = "http://localhost:8000"

def create_mock_audio_data():
    """Create mock audio data for testing."""
    # Create fake audio bytes (simulating a small audio file)
    mock_audio = b"MOCK_AUDIO_DATA_" + b"0" * 1024  # 1KB of mock data
    return mock_audio

def test_with_mock_audio():
    """Test submitting a response with mock audio data."""
    
    mock_audio = create_mock_audio_data()
    
    # For JSON payload, we need to encode bytes as base64
    audio_b64 = base64.b64encode(mock_audio).decode('utf-8')
    
    payload = {
        "session_token": "your-session-token-here",
        "response_text": "I have experience with microservices architecture and have deployed applications using Docker and Kubernetes.",
        "audio_data": audio_b64  # Base64 encoded audio data
    }
    
    headers = {
        "Authorization": "Bearer YOUR_JWT_TOKEN",
        "Content-Type": "application/json"
    }
    
    response = requests.post(
        f"{BASE_URL}/interviews/submit-response",
        json=payload,
        headers=headers
    )
    
    print("Status Code:", response.status_code)
    print("Response:", json.dumps(response.json(), indent=2))
    
    return response

def test_with_multipart_form():
    """Test using multipart form data (better for binary audio)."""
    
    mock_audio = create_mock_audio_data()
    
    # Using form data for binary upload
    data = {
        "session_token": "your-session-token-here",
        "response_text": "I've worked with real-time systems and WebSocket connections for live data streaming."
    }
    
    files = {
        "audio_data": ("audio.webm", mock_audio, "audio/webm")
    }
    
    headers = {
        "Authorization": "Bearer YOUR_JWT_TOKEN"
        # Don't set Content-Type for multipart - let requests handle it
    }
    
    response = requests.post(
        f"{BASE_URL}/interviews/submit-response",
        data=data,
        files=files,
        headers=headers
    )
    
    print("Status Code:", response.status_code)
    print("Response:", json.dumps(response.json(), indent=2))
    
    return response

if __name__ == "__main__":
    print("Testing with mock audio (JSON)...")
    test_with_mock_audio()
    
    print("\nTesting with multipart form...")
    test_with_multipart_form()
