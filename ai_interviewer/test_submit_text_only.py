"""
Test script for interview submit API - Text only
"""
import requests
import json

# API base URL
BASE_URL = "http://localhost:8000"  # Adjust port as needed

def test_text_only_submission():
    """Test submitting a response with only text."""
    
    # First, you'll need to:
    # 1. Register/login to get auth token
    # 2. Create an interview
    # 3. Start the interview to get session_token
    
    # Example payload for text-only submission
    payload = {
        "session_token": "your-session-token-here",
        "response_text": "I have 3 years of experience with Python, focusing on web development with FastAPI and Django. I've built several REST APIs and worked with databases like PostgreSQL.",
        # audio_data is optional - omit for text-only
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

if __name__ == "__main__":
    test_text_only_submission()
