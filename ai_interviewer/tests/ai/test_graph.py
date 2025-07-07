# DEPRECATED: Test for deprecated LangGraph system
# Tests now use the workflow system

from fastapi.testclient import TestClient
from src.ai_interviewer.main import app
import pytest
import asyncio

client = TestClient(app)

@pytest.mark.asyncio
async def test_interview_workflow():
    """Test the workflow system instead of deprecated graph system."""
    from src.ai_interviewer.ai.workflow import interview_workflow
    from src.ai_interviewer.interviews.schemas import LangGraphState
    
    # Test workflow initialization
    initial_state = LangGraphState(
        interview_id=1,
        session_token="",
        current_step="",
        user_id=1,
        position="Software Engineer",
        interview_type="technical",
        difficulty="medium"
    )
    
    # Test the workflow steps
    state = await interview_workflow.initialize_session(initial_state)
    assert state.session_token is not None
    assert state.should_continue is True
    
    state = await interview_workflow.generate_questions(state)
    assert state.questions_generated is not None
    assert len(state.questions_generated) > 0