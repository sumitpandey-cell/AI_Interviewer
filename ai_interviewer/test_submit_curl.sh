#!/bin/bash

# Test script for interview submit API using curl

# Base URL
BASE_URL="http://localhost:8000"

# You'll need to replace these with actual values:
SESSION_TOKEN="your-session-token-here"
JWT_TOKEN="your-jwt-token-here"

echo "Testing interview submit API..."

# Test 1: Text-only submission
echo "1. Testing text-only submission..."
curl -X POST "${BASE_URL}/interviews/submit-response" \
  -H "Authorization: Bearer ${JWT_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "session_token": "'${SESSION_TOKEN}'",
    "response_text": "I have extensive experience with Python and have worked on several machine learning projects using TensorFlow and PyTorch."
  }'

echo -e "\n\n"

# Test 2: With mock audio data (base64 encoded)
echo "2. Testing with mock audio data..."
MOCK_AUDIO_B64=$(echo -n "MOCK_AUDIO_DATA_FOR_TESTING" | base64)
curl -X POST "${BASE_URL}/interviews/submit-response" \
  -H "Authorization: Bearer ${JWT_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "session_token": "'${SESSION_TOKEN}'",
    "response_text": "I have experience building REST APIs and working with databases like PostgreSQL and MongoDB.",
    "audio_data": "'${MOCK_AUDIO_B64}'"
  }'

echo -e "\n\nDone!"
