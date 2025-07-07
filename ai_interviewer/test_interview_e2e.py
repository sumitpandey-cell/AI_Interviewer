"""
Complete end-to-end test for interview API
This script will:
1. Register a user (or login)
2. Create an interview
3. Start the interview
4. Submit responses (text-only and with mock audio)
5. Get results
"""
import requests
import json
import base64
import time

class InterviewAPITester:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.auth_token = None
        self.user_id = None
        self.interview_id = None
        self.session_token = None
    
    def register_user(self, username="testuser", email="test@example.com", password="testpass123"):
        """Register a new user."""
        try:
            response = self.session.post(f"{self.base_url}/auth/register", json={
                "username": username,
                "email": email,
                "password": password
            })
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get("access_token")
                self.user_id = data.get("user_id")
                self.session.headers.update({"Authorization": f"Bearer {self.auth_token}"})
                print("✅ User registered successfully")
                return True
            else:
                print(f"❌ Registration failed: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Registration error: {e}")
            return False
    
    def login_user(self, username="testuser", password="testpass123"):
        """Login existing user."""
        try:
            response = self.session.post(f"{self.base_url}/auth/login", data={
                "username": username,
                "password": password
            })
            if response.status_code == 200:
                data = response.json()
                self.auth_token = data.get("access_token")
                self.session.headers.update({"Authorization": f"Bearer {self.auth_token}"})
                print("✅ User logged in successfully")
                return True
            else:
                print(f"❌ Login failed: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Login error: {e}")
            return False
    
    def create_interview(self):
        """Create a new interview."""
        try:
            response = self.session.post(f"{self.base_url}/interviews/", json={
                "title": "Test Interview - Python Developer",
                "description": "Testing the interview API",
                "position": "Senior Python Developer",
                "company": "Test Company",
                "interview_type": "technical",
                "duration_minutes": 30
            })
            if response.status_code == 200:
                data = response.json()
                self.interview_id = data.get("id")
                print(f"✅ Interview created with ID: {self.interview_id}")
                return True
            else:
                print(f"❌ Interview creation failed: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Interview creation error: {e}")
            return False
    
    def start_interview(self):
        """Start the interview session."""
        try:
            response = self.session.post(f"{self.base_url}/interviews/start", json={
                "interview_id": self.interview_id
            })
            if response.status_code == 200:
                data = response.json()
                self.session_token = data.get("session_token")
                first_question = data.get("first_question", {})
                print(f"✅ Interview started with session: {self.session_token[:8]}...")
                print(f"📝 First question: {first_question.get('question', 'No question text')[:100]}...")
                return True
            else:
                print(f"❌ Interview start failed: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Interview start error: {e}")
            return False
    
    def submit_text_response(self, response_text):
        """Submit a text-only response."""
        try:
            response = self.session.post(f"{self.base_url}/interviews/submit-response", json={
                "session_token": self.session_token,
                "response_text": response_text
            })
            if response.status_code == 200:
                data = response.json()
                evaluation = data.get("evaluation", {})
                score = evaluation.get("score", 0)
                next_question = data.get("next_question")
                is_completed = data.get("is_completed", False)
                
                print(f"✅ Response submitted successfully")
                print(f"📊 Score: {score}/10")
                print(f"💬 Feedback: {evaluation.get('feedback', 'No feedback')[:100]}...")
                
                if is_completed:
                    print("🏁 Interview completed!")
                    return False  # No more questions
                elif next_question:
                    print(f"❓ Next question: {next_question.get('question', 'No question')[:100]}...")
                    return True  # Continue
                else:
                    print("⚠️ No next question provided")
                    return False
                    
            else:
                print(f"❌ Response submission failed: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Response submission error: {e}")
            return False
    
    def submit_audio_response(self, response_text, mock_audio_size=1024):
        """Submit a response with mock audio data."""
        try:
            # Create mock audio data
            mock_audio = b"MOCK_AUDIO_" + b"0" * mock_audio_size
            audio_b64 = base64.b64encode(mock_audio).decode('utf-8')
            
            response = self.session.post(f"{self.base_url}/interviews/submit-response", json={
                "session_token": self.session_token,
                "response_text": response_text,
                "audio_data": audio_b64
            })
            
            if response.status_code == 200:
                data = response.json()
                evaluation = data.get("evaluation", {})
                score = evaluation.get("score", 0)
                next_question = data.get("next_question")
                is_completed = data.get("is_completed", False)
                
                print(f"✅ Audio response submitted successfully")
                print(f"📊 Score: {score}/10")
                print(f"💬 Feedback: {evaluation.get('feedback', 'No feedback')[:100]}...")
                print(f"🎵 Audio processed: {len(mock_audio)} bytes")
                
                if is_completed:
                    print("🏁 Interview completed!")
                    return False
                elif next_question:
                    print(f"❓ Next question: {next_question.get('question', 'No question')[:100]}...")
                    return True
                else:
                    print("⚠️ No next question provided")
                    return False
                    
            else:
                print(f"❌ Audio response submission failed: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Audio response submission error: {e}")
            return False
    
    def get_interview_results(self):
        """Get final interview results."""
        try:
            response = self.session.get(f"{self.base_url}/interviews/{self.interview_id}/results")
            if response.status_code == 200:
                data = response.json()
                print("✅ Interview results retrieved:")
                print(f"📋 Title: {data.get('title')}")
                print(f"📊 Final Score: {data.get('score')}")
                print(f"⏱️ Duration: {data.get('duration_minutes')} minutes")
                print(f"❓ Questions Answered: {data.get('questions_answered')}")
                return True
            else:
                print(f"❌ Failed to get results: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Results retrieval error: {e}")
            return False
    
    def run_full_test(self):
        """Run the complete test suite."""
        print("🚀 Starting Interview API Test Suite")
        print("=" * 50)
        
        # Step 1: Authentication
        print("\n1. 👤 Authenticating...")
        if not self.register_user():
            if not self.login_user():
                print("❌ Authentication failed, stopping test")
                return False
        
        # Step 2: Create Interview
        print("\n2. 📝 Creating interview...")
        if not self.create_interview():
            print("❌ Interview creation failed, stopping test")
            return False
        
        # Step 3: Start Interview
        print("\n3. ▶️ Starting interview...")
        if not self.start_interview():
            print("❌ Interview start failed, stopping test")
            return False
        
        # Step 4: Submit responses
        print("\n4. 💭 Submitting responses...")
        
        responses = [
            "I have 5 years of experience with Python, specializing in web development with Django and FastAPI. I've built several REST APIs and worked extensively with PostgreSQL databases.",
            "I'm proficient in object-oriented programming, design patterns, and have experience with microservices architecture. I've also worked with Docker and Kubernetes for containerization.",
            "My experience includes working with real-time systems using WebSockets, implementing caching with Redis, and building scalable applications that handle high traffic loads."
        ]
        
        for i, response_text in enumerate(responses):
            print(f"\n   Response {i+1}:")
            
            if i % 2 == 0:  # Alternate between text-only and audio
                should_continue = self.submit_text_response(response_text)
            else:
                should_continue = self.submit_audio_response(response_text)
            
            if not should_continue:
                print("   Interview ended")
                break
            
            time.sleep(1)  # Brief pause between responses
        
        # Step 5: Get Results
        print("\n5. 📊 Getting results...")
        self.get_interview_results()
        
        print("\n✅ Test suite completed!")
        return True

def main():
    """Run the test."""
    tester = InterviewAPITester()
    tester.run_full_test()

if __name__ == "__main__":
    main()
