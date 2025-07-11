"""
Route for handling question retry
"""

from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional

from ..database.session import get_db
from ..auth.dependencies import get_current_active_user
from ..auth.models import User
from ..interviews import service as interview_service
from ..utilities.Text_to_speech.tts_service import get_tts_service
from ..interviews.schemas import LangGraphState

router = APIRouter()
tts_service = get_tts_service()

def safe_restore_state(state_dict):
    """Safely restore LangGraphState from database, cleaning any problematic data."""
    # Remove any fields that could cause serialization issues
    clean_dict = state_dict.copy() if state_dict else {}
    
    # Remove binary data fields that shouldn't be in the database but might be there
    binary_fields = {'audio_data', 'video_data', 'temp_data'}
    for field in binary_fields:
        if field in clean_dict:
            del clean_dict[field]
    
    # Convert any string representations of binary data back to None
    for key, value in clean_dict.items():
        if isinstance(value, str) and value.startswith('<binary_data:'):
            clean_dict[key] = None
        elif isinstance(value, str) and value.startswith('<audio_bytes:'):
            clean_dict[key] = None
    
    try:
        return LangGraphState(**clean_dict)
    except Exception as e:
        # In case of schema incompatibility, do basic recovery
        print(f"State restoration error: {e}")
        # Provide minimal viable state
        return LangGraphState(
            interview_id=clean_dict.get('interview_id', 0),
            session_token=clean_dict.get('session_token', ''),
            current_step=clean_dict.get('current_step', 'error'),
            user_id=clean_dict.get('user_id', 0),
            interview_type=clean_dict.get('interview_type', 'technical'),
            position=clean_dict.get('position', 'Developer'),
        )

@router.post("/session/{session_token}/retry-question")
async def retry_question(
    session_token: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Retry or rephrase the current question."""
    service = interview_service.InterviewService(db)
    
    # Get session
    session = db.query(interview_service.models.InterviewSession).filter(
        interview_service.models.InterviewSession.session_token == session_token,
        interview_service.models.InterviewSession.is_active == True
    ).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found or inactive")
    
    # Get current state
    state_dict = session.workflow_state or {}
    state = safe_restore_state(state_dict)
    
    # Get current question to rephrase
    current_question = state.current_question
    if not current_question:
        raise HTTPException(status_code=400, detail="No current question to retry")
    
    # Extract question text
    question_text = ''
    if isinstance(current_question, dict) and 'question' in current_question:
        question_text = current_question['question']
    elif isinstance(current_question, str):
        question_text = current_question
    else:
        question_text = str(current_question)
        
    # Create rephrased version by adding prefix
    rephrased_question = f"Let me rephrase: {question_text}"
    
    # Generate audio for the rephrased question if TTS available
    audio_data = None
    if tts_service:
        try:
            audio_data = tts_service.synthesize_speech(rephrased_question)
        except Exception as e:
            print(f"Failed to generate audio for rephrased question: {e}")
    
    return {
        "rephrased_question": rephrased_question,
        "audio_data": audio_data
    }
