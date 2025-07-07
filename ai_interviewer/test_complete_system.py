"""
Comprehensive test script for the AI Interviewer backend
"""

import asyncio
import json
import requests
from datetime import datetime

# Test configuration
BASE_URL = "http://localhost:8000"
TEST_USER = {
    "username": "testuser",
    "email": "test@example.com",
    "password": "testpassword123"
}

class AIInterviewerTest:
    def __init__(self):
        self.base_url = BASE_URL
        self.access_token = None
        self.interview_id = None
        self.session_token = None
    
    def make_request(self, method, endpoint, data=None, files=None, headers=None):
        """Make HTTP request with error handling."""
        url = f"{self.base_url}{endpoint}"
        
        default_headers = {}
        if self.access_token:
            default_headers["Authorization"] = f"Bearer {self.access_token}"
        
        if headers:
            default_headers.update(headers)
        
        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=default_headers)
            elif method.upper() == "POST":
                if files:
                    response = requests.post(url, data=data, files=files, headers=default_headers)
                else:
                    response = requests.post(url, json=data, headers=default_headers)
            elif method.upper() == "DELETE":
                response = requests.delete(url, headers=default_headers)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            return response
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            return None
    
    def test_health_check(self):
        """Test health check endpoint."""
        print("\\n=== Testing Health Check ===")
        response = self.make_request("GET", "/health")
        
        if response and response.status_code == 200:
            print("✅ Health check passed")
            print(f"Response: {response.json()}")
            return True
        else:
            print("❌ Health check failed")
            return False
    
    def test_user_registration(self):
        """Test user registration."""
        print("\\n=== Testing User Registration ===")
        response = self.make_request("POST", "/auth/register", data=TEST_USER)
        
        if response and response.status_code == 201:
            print("✅ User registration successful")
            print(f"Response: {response.json()}")
            return True
        elif response and response.status_code == 400:
            print("⚠️ User may already exist")
            return True  # Proceed with login
        else:
            print("❌ User registration failed")
            if response:
                print(f"Status: {response.status_code}, Response: {response.text}")
            return False
    
    def test_user_login(self):
        """Test user login."""
        print("\\n=== Testing User Login ===")
        login_data = {
            "username": TEST_USER["username"],
            "password": TEST_USER["password"]
        }
        
        response = self.make_request("POST", "/auth/login", data=login_data)
        
        if response and response.status_code == 200:
            data = response.json()
            self.access_token = data.get("access_token")
            print("✅ User login successful")
            print(f"Access token received: {self.access_token[:20]}...")
            return True
        else:
            print("❌ User login failed")
            if response:
                print(f"Status: {response.status_code}, Response: {response.text}")
            return False
    
    def test_create_interview(self):
        """Test interview creation."""
        print("\\n=== Testing Interview Creation ===")
        interview_data = {
            "title": "Python Developer Interview",
            "description": "Technical interview for Python developer position",
            "position": "Senior Python Developer",
            "company": "Tech Corp",
            "interview_type": "technical",
            "duration_minutes": 45
        }
        
        response = self.make_request("POST", "/interviews/", data=interview_data)
        
        if response and response.status_code == 200:
            data = response.json()
            self.interview_id = data.get("id")
            print("✅ Interview created successfully")
            print(f"Interview ID: {self.interview_id}")
            print(f"Interview details: {json.dumps(data, indent=2)}")
            return True
        else:
            print("❌ Interview creation failed")
            if response:
                print(f"Status: {response.status_code}, Response: {response.text}")
            return False
    
    def test_start_interview(self):
        """Test starting an interview session."""
        print("\\n=== Testing Interview Start ===")
        if not self.interview_id:
            print("❌ No interview ID available")
            return False
        
        response = self.make_request("POST", f"/interviews/{self.interview_id}/start")
        
        if response and response.status_code == 200:
            data = response.json()
            self.session_token = data.get("session_token")
            print("✅ Interview started successfully")
            print(f"Session token: {self.session_token}")
            print(f"First question: {data.get('first_question', {}).get('question', 'No question')}")
            return True
        else:
            print("❌ Interview start failed")
            if response:
                print(f"Status: {response.status_code}, Response: {response.text}")
            return False
    
    def test_submit_response(self):
        """Test submitting a response."""
        print("\\n=== Testing Response Submission ===")
        if not self.session_token:
            print("❌ No session token available")
            return False
        
        response_data = {
            "session_token": self.session_token,
            "response_text": "I have 5 years of Python experience, including Django, Flask, and FastAPI frameworks. I've worked on REST APIs, database design, and cloud deployments."
        }
        
        response = self.make_request("POST", "/interviews/session/submit", data=response_data)
        
        if response and response.status_code == 200:
            data = response.json()
            print("✅ Response submitted successfully")
            print(f"Evaluation score: {data.get('evaluation', {}).get('score', 'N/A')}")
            print(f"Feedback: {data.get('evaluation', {}).get('feedback', 'No feedback')}")
            print(f"Next question: {data.get('next_question', {}).get('question', 'No next question')}")
            return True
        else:
            print("❌ Response submission failed")
            if response:
                print(f"Status: {response.status_code}, Response: {response.text}")
            return False
    
    def test_session_status(self):
        """Test getting session status."""
        print("\\n=== Testing Session Status ===")
        if not self.session_token:
            print("❌ No session token available")
            return False
        
        response = self.make_request("GET", f"/interviews/session/{self.session_token}/status")
        
        if response and response.status_code == 200:
            data = response.json()
            print("✅ Session status retrieved")
            print(f"Status: {json.dumps(data, indent=2)}")
            return True
        else:
            print("❌ Session status retrieval failed")
            if response:
                print(f"Status: {response.status_code}, Response: {response.text}")
            return False
    
    def test_pause_resume_session(self):
        """Test pausing and resuming a session."""
        print("\\n=== Testing Session Pause/Resume ===")
        if not self.session_token:
            print("❌ No session token available")
            return False
        
        # Test pause
        response = self.make_request("POST", f"/interviews/session/{self.session_token}/pause")
        if response and response.status_code == 200:
            print("✅ Session paused successfully")
        else:
            print("❌ Session pause failed")
            return False
        
        # Test resume
        response = self.make_request("POST", f"/interviews/session/{self.session_token}/resume")
        if response and response.status_code == 200:
            print("✅ Session resumed successfully")
            return True
        else:
            print("❌ Session resume failed")
            return False
    
    def test_get_interviews(self):
        """Test getting user interviews."""
        print("\\n=== Testing Get User Interviews ===")
        response = self.make_request("GET", "/interviews/")
        
        if response and response.status_code == 200:
            data = response.json()
            print("✅ Interviews retrieved successfully")
            print(f"Number of interviews: {len(data)}")
            for interview in data:
                print(f"  - {interview.get('title')} (Status: {interview.get('status')})")
            return True
        else:
            print("❌ Interview retrieval failed")
            if response:
                print(f"Status: {response.status_code}, Response: {response.text}")
            return False
    
    def run_all_tests(self):
        """Run all tests in sequence."""
        print("🚀 Starting AI Interviewer Backend Tests")
        print("=" * 50)
        
        tests = [
            self.test_health_check,
            self.test_user_registration,
            self.test_user_login,
            self.test_create_interview,
            self.test_start_interview,
            self.test_submit_response,
            self.test_session_status,
            self.test_pause_resume_session,
            self.test_get_interviews
        ]
        
        passed = 0
        failed = 0
        
        for test in tests:
            try:
                if test():
                    passed += 1
                else:
                    failed += 1
            except Exception as e:
                print(f"❌ Test {test.__name__} crashed: {e}")
                failed += 1
        
        print("\\n" + "=" * 50)
        print(f"🏁 Test Results: {passed} passed, {failed} failed")
        
        if failed == 0:
            print("🎉 All tests passed! The system is working correctly.")
        else:
            print("⚠️ Some tests failed. Check the output above for details.")
        
        return failed == 0


if __name__ == "__main__":
    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code != 200:
            print("❌ Server is not responding properly")
            print("Please start the server with: python -m uvicorn src.ai_interviewer.main_simple:app --reload")
            exit(1)
    except requests.exceptions.RequestException:
        print("❌ Cannot connect to server")
        print("Please start the server with: python -m uvicorn src.ai_interviewer.main_simple:app --reload")
        exit(1)
    
    # Run tests
    tester = AIInterviewerTest()
    success = tester.run_all_tests()
    exit(0 if success else 1)
