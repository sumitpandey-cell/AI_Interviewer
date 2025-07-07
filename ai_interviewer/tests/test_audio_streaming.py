"""
Test for real-time audio streaming functionality
"""
import sys
from pathlib import Path

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import pytest
from ai_interviewer.interviews import schemas


def test_submit_response_with_audio_data():
    """Test that SubmitResponseRequest works with audio_data instead of audio_file_url."""
    # Test with audio data
    request_with_audio = schemas.SubmitResponseRequest(
        session_token="test-session-123",
        response_text="This is my response",
        audio_data=b"fake audio bytes"
    )
    
    assert request_with_audio.session_token == "test-session-123"
    assert request_with_audio.response_text == "This is my response"
    assert request_with_audio.audio_data == b"fake audio bytes"
    
    # Test without audio data
    request_without_audio = schemas.SubmitResponseRequest(
        session_token="test-session-456",
        response_text="Text only response"
    )
    
    assert request_without_audio.session_token == "test-session-456"
    assert request_without_audio.response_text == "Text only response"
    assert request_without_audio.audio_data is None


def test_complete_response_with_audio_data():
    """Test that CompleteResponseRequest works with audio_data."""
    request = schemas.CompleteResponseRequest(
        response_text="Complete response",
        audio_data=b"complete audio data",
        include_analysis=True,
        include_insights=True
    )
    
    assert request.response_text == "Complete response"
    assert request.audio_data == b"complete audio data"
    assert request.include_analysis is True
    assert request.include_insights is True


def test_lang_graph_state_with_audio_data():
    """Test that LangGraphState works with audio_data instead of audio_url."""
    state = schemas.LangGraphState(
        interview_id=1,
        session_token="test-session",
        current_step="audio_processing",
        user_id=123,
        interview_type="technical",
        position="Software Engineer",
        audio_data=b"stream audio data",
        audio_format="webm"
    )
    
    assert state.interview_id == 1
    assert state.session_token == "test-session"
    assert state.audio_data == b"stream audio data"
    assert state.audio_format == "webm"
    # Ensure no audio_url attribute exists
    assert not hasattr(state, 'audio_url')


def test_demo_workflow_with_audio_data():
    """Test that DemoWorkflowRequest works with audio_data."""
    demo_request = schemas.DemoWorkflowRequest(
        interview_type="behavioral",
        position="Product Manager",
        difficulty="hard",
        sample_response="Sample demo response",
        audio_data=b"demo audio stream"
    )
    
    assert demo_request.interview_type == "behavioral"
    assert demo_request.position == "Product Manager"
    assert demo_request.difficulty == "hard"
    assert demo_request.sample_response == "Sample demo response"
    assert demo_request.audio_data == b"demo audio stream"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
