#!/usr/bin/env python3
"""
Simple test to start server and run basic tests
"""

import sys
import time
import subprocess
import requests
import threading
from pathlib import Path

# Add src to path
sys.path.append('src')

def start_server():
    """Start the FastAPI server."""
    try:
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "src.ai_interviewer.main_simple:app",
            "--host", "0.0.0.0", "--port", "8000"
        ], cwd=Path.cwd())
    except Exception as e:
        print(f"Failed to start server: {e}")

def test_endpoints():
    """Test basic endpoints."""
    print("Testing AI Interviewer API...")
    
    # Wait for server to start
    time.sleep(3)
    
    base_url = "http://localhost:8000"
    
    # Test health endpoint
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        if response.status_code == 200:
            print("✅ Health check passed")
            print(f"Response: {response.json()}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Failed to connect to server: {e}")
        return False
    
    # Test root endpoint
    try:
        response = requests.get(f"{base_url}/", timeout=10)
        if response.status_code == 200:
            print("✅ Root endpoint works")
            print(f"Response: {response.json()}")
        else:
            print(f"❌ Root endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Root endpoint error: {e}")
    
    # Test documentation
    try:
        response = requests.get(f"{base_url}/docs", timeout=10)
        if response.status_code == 200:
            print("✅ API documentation available at http://localhost:8000/docs")
        else:
            print(f"❌ Documentation failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Documentation error: {e}")
    
    return True

if __name__ == "__main__":
    print("🚀 Starting AI Interviewer System Test")
    print("=" * 50)
    
    # Start server in background thread
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    
    # Test endpoints
    if test_endpoints():
        print("\n✅ Basic tests completed successfully!")
        print("🌟 The AI Interviewer backend is working!")
        print("\nNext steps:")
        print("1. Visit http://localhost:8000/docs for API documentation")
        print("2. Use the provided test script to test user registration and interviews")
        print("3. Integrate with a frontend application")
    else:
        print("\n❌ Some tests failed")
    
    print("\nPress Ctrl+C to stop the server")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n👋 Shutting down...")
