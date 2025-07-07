from fastapi.testclient import TestClient
from src.ai_interviewer.main import app
from src.ai_interviewer.ai.service import generate_questions, evaluate_response

client = TestClient(app)

def test_generate_questions():
    response = client.post("/ai/questions", json={"job_role": "Software Engineer", "difficulty": "Intermediate"})
    assert response.status_code == 200
    assert len(response.json()) == 5

def test_evaluate_response():
    result = evaluate_response("This is a sample response.", "What is Python?")
    assert "score" in result
    assert "feedback" in result