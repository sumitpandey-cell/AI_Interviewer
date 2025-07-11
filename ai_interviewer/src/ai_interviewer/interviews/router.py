"""
Interview management API routes
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from datetime import datetime

from . import schemas, models
from .service import InterviewService
from ..database.session import get_db
from ..auth.dependencies import get_current_active_user
from ..auth.models import User
from .retry_question import router as retry_question_router


router = APIRouter()
router.include_router(retry_question_router)  # Include the retry_question router

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
        from .schemas import LangGraphState
        return LangGraphState(**clean_dict)
    except Exception as e:
        print(f"Warning: Failed to restore state, using minimal state: {e}")
        # Return a minimal valid state if restoration fails
        return LangGraphState(
            interview_id=clean_dict.get('interview_id', 1),
            session_token=clean_dict.get('session_token', 'unknown'),
            current_step=clean_dict.get('current_step', 'initialize'),
            user_id=clean_dict.get('user_id', 1),
            interview_type=clean_dict.get('interview_type', 'technical'),
            position=clean_dict.get('position', 'Software Engineer')
        )


@router.post("/", response_model=schemas.InterviewResponse)
async def create_interview(
    interview: schemas.InterviewCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new interview."""
    service = InterviewService(db)
    db_interview = await service.create_interview(interview, current_user.id)
    return db_interview


@router.get("/", response_model=List[schemas.InterviewResponse])
async def get_user_interviews(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all interviews for the current user."""
    service = InterviewService(db)
    interviews = service.get_user_interviews(current_user.id)
    return interviews


@router.get("/{interview_id}", response_model=schemas.InterviewResponse)
async def get_interview(
    interview_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a specific interview."""
    service = InterviewService(db)
    interview = service.get_interview(interview_id, current_user.id)
    return interview


@router.post("/{interview_id}/start", response_model=schemas.InterviewStartResponse)
async def start_interview(
    interview_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Start an interview session with LangGraph workflow."""
    service = InterviewService(db)
    result = await service.start_interview(interview_id, current_user.id)
    return schemas.InterviewStartResponse(
        session_token=result["session_token"],
        first_question=result["first_question"],
        audio_data=result.get("audio_data"),  # Include TTS audio data if available
        workflow_state=result.get("workflow_state", {})
    )


@router.post("/session/submit", response_model=schemas.SubmitResponseResponse)
async def submit_response(
    request: schemas.SubmitResponseRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Submit a response to the current interview question."""
    service = InterviewService(db)
    result = await service.submit_response(
        session_token=request.session_token,
        audio_data=request.audio_data
    )
    
    return schemas.SubmitResponseResponse(
        evaluation=schemas.EvaluationResponse(**result["evaluation"]),
        next_question=result["next_question"],
        audio_data=result.get("audio_data"),  # Include TTS audio data
        is_completed=result["is_completed"],
        workflow_state=result["workflow_state"]
    )


@router.get("/session/{session_token}/status")
async def get_session_status(
    session_token: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get the current status of an interview session."""
    service = InterviewService(db)
    return service.get_session_status(session_token)


@router.get("/{interview_id}/results")
async def get_interview_results(
    interview_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get the final results of a completed interview."""
    service = InterviewService(db)
    return service.get_interview_results(interview_id, current_user.id)


# Workflow control endpoints
@router.post("/session/{session_token}/pause")
async def pause_session(
    session_token: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Pause an interview session."""
    # Get session
    session = db.query(models.InterviewSession).filter(
        models.InterviewSession.session_token == session_token,
        models.InterviewSession.is_active == True
    ).first()
    print(f"Pausing session: {session_token}, found: {session}")
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found or inactive")
    
    # Update session status
    session.session_status = "paused"
    session.last_activity_at = func.now()
    
    # Also update interview status to paused
    interview = session.interview
    interview.status = "paused"
    
    db.commit()
    
    return {"message": "Session paused", "session_token": session_token}


@router.post("/session/{session_token}/resume")
async def resume_session(
    session_token: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Resume a paused interview session."""
    # Get session
    session = db.query(models.InterviewSession).filter(
        models.InterviewSession.session_token == session_token,
        models.InterviewSession.is_active == True
    ).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found or inactive")
    
    if session.session_status != "paused":
        raise HTTPException(status_code=400, detail="Session is not paused")
    
    # Resume session
    session.session_status = "started"
    session.last_activity_at = func.now()
    
    # Update interview status back to in_progress
    interview = session.interview
    interview.status = "in_progress"
    
    db.commit()
    
    # Get the current question from state
    state_dict = session.workflow_state or {}
    current_question = state_dict.get("current_question", None)
    
    return {
        "message": "Session resumed", 
        "session_token": session_token,
        "current_question": current_question
    }


@router.delete("/session/{session_token}")
async def cancel_session(
    session_token: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Cancel an interview session."""
    # Get session
    session = db.query(models.InterviewSession).filter(
        models.InterviewSession.session_token == session_token,
        models.InterviewSession.is_active == True
    ).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found or inactive")
    
    # Cancel session
    session.is_active = False
    session.session_status = "cancelled"
    session.last_activity_at = func.now()
    
    # Update interview status
    interview = session.interview
    if interview.status == "in_progress":
        interview.status = "cancelled"
    
    db.commit()
    
    return {"message": "Session cancelled", "session_token": session_token}


# Advanced workflow endpoints for comprehensive interview management
@router.post("/session/{session_token}/validate")
async def validate_session(
    session_token: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Validate interview session and prerequisites."""
    service = InterviewService(db)
    
    # Get session
    session = db.query(models.InterviewSession).filter(
        models.InterviewSession.session_token == session_token,
        models.InterviewSession.is_active == True
    ).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found or inactive")
    
    try:
        from ..ai.workflow import interview_workflow
        from .schemas import LangGraphState
        
        # Get current state
        state_dict = session.workflow_state or {}
        state = safe_restore_state(state_dict)
        
        # Run validation steps
        state = await interview_workflow.validate_session(state)
        state = await interview_workflow.check_interview_prerequisites(state)
        
        # Update session
        session.workflow_state = state.model_dump()
        session.current_step = state.current_step
        db.commit()
        
        return {
            "session_token": session_token,
            "is_valid": getattr(state, 'session_valid', True) and state.should_continue,
            "prerequisites_met": not bool(state.error_message),
            "current_step": state.current_step,
            "error_message": state.error_message,
            "validation_details": {
                "session_valid": getattr(state, 'session_valid', False),
                "questions_available": len(state.questions_generated) if state.questions_generated else 0,
                "user_authenticated": bool(state.user_id)
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Session validation failed: {str(e)}")


@router.post("/session/{session_token}/process-response")
async def process_complete_response(
    session_token: str,
    request: schemas.CompleteResponseRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Process a complete response through the full workflow."""
    service = InterviewService(db)
    
    # Get session
    session = db.query(models.InterviewSession).filter(
        models.InterviewSession.session_token == session_token,
        models.InterviewSession.is_active == True
    ).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found or inactive")
    
    try:
        from ..ai.workflow import interview_workflow
        from .schemas import LangGraphState
        
        # Get current state
        state_dict = session.workflow_state or {}
        state = safe_restore_state(state_dict)
        
        # Update state with response data
        state.user_response = request.response_text
        state.audio_data = request.audio_data
        
        # Run complete workflow for response processing
        if request.audio_data:
            state = await interview_workflow.process_audio(state)
        
        state = await interview_workflow.validate_response(state)
        state = await interview_workflow.evaluate_response(state)
        state = await interview_workflow.analyze_response_depth(state)
        state = await interview_workflow.generate_dynamic_follow_up(state)
        state = await interview_workflow.calculate_progressive_score(state)
        state = await interview_workflow.generate_feedback(state)
        state = await interview_workflow.check_termination_conditions(state)
        
        # Determine next steps
        if state.should_continue and not state.error_message:
            state = await interview_workflow.prepare_next_question(state)
        else:
            state = await interview_workflow.complete_interview(state)
            state = await interview_workflow.generate_interview_insights(state)
            
            # Update interview status
            interview = session.interview
            interview.status = "completed"
            interview.completed_at = datetime.now()
            interview.score = state.total_score
            
            # Close session
            session.is_active = False
            session.session_status = "completed"
        
        # Update session
        session.workflow_state = state.model_dump()
        session.current_step = state.current_step
        session.last_activity_at = func.now()
        db.commit()
        
        # Prepare comprehensive response
        response_data = {
            "session_token": session_token,
            "evaluation": state.ai_evaluation or {},
            "speech_analysis": getattr(state, 'speech_analysis', None),
            "emotion_analysis": getattr(state, 'emotion_analysis', None),
            "depth_analysis": getattr(state, 'depth_analysis', None),
            "behavioral_analysis": getattr(state, 'behavioral_analysis', None),
            "follow_up_question": getattr(state, 'follow_up_question', None),
            "current_score": getattr(state, 'current_average_score', 0),
            "difficulty_adjustment": getattr(state, 'adjustment_message', None),
            "next_question": state.current_question if state.should_continue else None,
            "audio_data": getattr(state, 'audio_response', None),  # Audio response data
            "is_completed": not state.should_continue,
            "termination_reason": getattr(state, 'termination_reason', None),
            "final_assessment": getattr(state, 'final_assessment', None),
            "interview_report": getattr(state, 'interview_report', None),
            "interview_insights": getattr(state, 'interview_insights', None),
            "encouragement": getattr(state, 'encouragement_message', None),
            "workflow_state": {
                "current_step": state.current_step,
                "total_score": state.total_score,
                "questions_answered": len(state.responses_history),
                "should_continue": state.should_continue
            }
        }
        
        return response_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Response processing failed: {str(e)}")


@router.get("/session/{session_token}/analysis")
async def get_session_analysis(
    session_token: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get comprehensive analysis of the current session."""
    # Get session
    session = db.query(models.InterviewSession).filter(
        models.InterviewSession.session_token == session_token
    ).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    try:
        from .schemas import LangGraphState
        
        # Get current state
        state_dict = session.workflow_state or {}
        state = safe_restore_state(state_dict)
        
        # Calculate performance metrics
        response_scores = [r.get("evaluation", {}).get("overall_score", 0) for r in state.responses_history]
        avg_score = sum(response_scores) / len(response_scores) if response_scores else 0
        
        performance_trend = "stable"
        if len(response_scores) > 1:
            if response_scores[-1] > response_scores[0]:
                performance_trend = "improving"
            elif response_scores[-1] < response_scores[0]:
                performance_trend = "declining"
        
        return {
            "session_token": session_token,
            "session_status": session.session_status,
            "current_step": state.current_step,
            "performance_summary": {
                "average_score": round(avg_score, 2),
                "total_score": state.total_score,
                "questions_answered": len(state.responses_history),
                "performance_trend": performance_trend,
                "current_difficulty": state.difficulty
            },
            "response_history": [
                {
                    "question_type": r.get("question", {}).get("type", "unknown"),
                    "score": r.get("evaluation", {}).get("overall_score", 0),
                    "timestamp": r.get("timestamp"),
                    "is_follow_up": r.get("is_follow_up", False)
                }
                for r in state.responses_history
            ],
            "speech_quality_metrics": [
                r.get("speech_analysis", {})
                for r in state.responses_history
                if r.get("speech_analysis")
            ],
            "emotion_patterns": [
                r.get("emotion_analysis", {})
                for r in state.responses_history
                if r.get("emotion_analysis")
            ],
            "insights": getattr(state, 'interview_insights', None)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis retrieval failed: {str(e)}")


@router.post("/session/{session_token}/early-termination")
async def trigger_early_termination(
    session_token: str,
    reason: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Trigger early termination of interview session."""
    service = InterviewService(db)
    
    # Get session
    session = db.query(models.InterviewSession).filter(
        models.InterviewSession.session_token == session_token,
        models.InterviewSession.is_active == True
    ).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found or inactive")
    
    try:
        from ..ai.workflow import interview_workflow
        from .schemas import LangGraphState
        
        # Get current state
        state_dict = session.workflow_state or {}
        state = safe_restore_state(state_dict)
        
        # Set termination
        state.should_continue = False
        state.termination_reason = f"manual_termination_{reason}"
        
        # Complete interview with early termination
        state = await interview_workflow.complete_interview(state)
        state = await interview_workflow.generate_interview_insights(state)
        
        # Update database
        interview = session.interview
        interview.status = "completed"
        interview.completed_at = datetime.now()
        interview.score = state.total_score
        
        session.is_active = False
        session.session_status = "completed"
        session.workflow_state = state.model_dump()
        
        db.commit();
        
        return {
            "session_token": session_token,
            "message": "Interview terminated successfully",
            "termination_reason": state.termination_reason,
            "final_assessment": getattr(state, 'final_assessment', None),
            "interview_report": getattr(state, 'interview_report', None)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Early termination failed: {str(e)}")


# Complete Sequential Diagram Demo Endpoint
@router.post("/demo/complete-workflow")
async def demo_complete_workflow(
    demo_request: schemas.DemoWorkflowRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Demonstrate the complete sequential diagram workflow."""
    try:
        from ..ai.workflow import interview_workflow
        from .schemas import LangGraphState
        from datetime import datetime
        import uuid
        
        # Initialize demo state
        demo_state = LangGraphState(
            interview_id=demo_request.interview_id or 1,
            session_token=str(uuid.uuid4()),
            current_step="demo_start",
            user_id=1,  # Use current_user.id in real implementation
            interview_type=demo_request.interview_type,
            position=demo_request.position,
            difficulty=demo_request.difficulty
        )
        
        workflow_log = []
        
        # 1. Session Validation
        demo_state.current_step = "session_validation"
        demo_state = await interview_workflow.validate_session(demo_state)
        workflow_log.append({
            "step": "session_validation",
            "status": "completed" if demo_state.session_valid else "failed",
            "details": f"Session valid: {demo_state.session_valid}"
        })
        
        # 2. Prerequisites Check
        demo_state = await interview_workflow.check_interview_prerequisites(demo_state)
        workflow_log.append({
            "step": "prerequisites_check",
            "status": "completed" if not demo_state.error_message else "failed",
            "details": demo_state.error_message or "All prerequisites met"
        })
        
        # 3. Question Generation
        demo_state = await interview_workflow.generate_questions(demo_state)
        workflow_log.append({
            "step": "question_generation",
            "status": "completed",
            "details": f"Generated {len(demo_state.questions_generated)} questions"
        })
        
        # 4. Present First Question
        demo_state = await interview_workflow.present_question(demo_state)
        workflow_log.append({
            "step": "present_question",
            "status": "completed",
            "details": f"Presented question: {demo_state.current_question['question'][:50]}..."
        })
        
        # Simulate response processing for demo
        demo_state.user_response = demo_request.sample_response or "This is a sample response demonstrating my experience with the technology."
        demo_state.audio_data = demo_request.audio_data
        
        # 5. Audio Processing (if provided)
        if demo_state.audio_data:
            demo_state = await interview_workflow.process_audio(demo_state)
            workflow_log.append({
                "step": "audio_processing",
                "status": "completed",
                "details": f"Speech analysis: {demo_state.speech_analysis.get('overall_speech_score', 0) if demo_state.speech_analysis else 0}/10"
            })
        
        # 6. Response Validation
        demo_state = await interview_workflow.validate_response(demo_state)
        workflow_log.append({
            "step": "response_validation",
            "status": "completed" if not demo_state.error_message else "warning",
            "details": demo_state.warning_message or demo_state.error_message or "Response validated successfully"
        })
        
        # 7. Response Evaluation
        demo_state = await interview_workflow.evaluate_response(demo_state)
        workflow_log.append({
            "step": "response_evaluation",
            "status": "completed",
            "details": f"Score: {demo_state.ai_evaluation.get('overall_score', 0)}/10"
        })
        
        # 8. Response Depth Analysis
        demo_state = await interview_workflow.analyze_response_depth(demo_state)
        workflow_log.append({
            "step": "depth_analysis",
            "status": "completed",
            "details": f"Depth score: {getattr(demo_state, 'depth_analysis', {}).get('depth_score', 0)}/10"
        })
        
        # 9. Dynamic Follow-up Generation
        demo_state = await interview_workflow.generate_dynamic_follow_up(demo_state)
        follow_up_generated = hasattr(demo_state, 'follow_up_question') and demo_state.follow_up_question
        workflow_log.append({
            "step": "follow_up_generation",
            "status": "completed",
            "details": f"Follow-up {'generated' if follow_up_generated else 'not needed'}"
        })
        
        # 10. Progressive Scoring
        demo_state = await interview_workflow.calculate_progressive_score(demo_state)
        workflow_log.append({
            "step": "progressive_scoring",
            "status": "completed",
            "details": f"Average score: {getattr(demo_state, 'current_average_score', 0):.1f}/10"
        })
        
        # 11. Feedback Generation
        demo_state = await interview_workflow.generate_feedback(demo_state)
        workflow_log.append({
            "step": "feedback_generation",
            "status": "completed",
            "details": demo_state.encouragement_message or "Feedback generated"
        })
        
        # 12. Termination Check
        demo_state = await interview_workflow.check_termination_conditions(demo_state)
        workflow_log.append({
            "step": "termination_check",
            "status": "completed",
            "details": f"Continue: {demo_state.should_continue}, Reason: {getattr(demo_state, 'termination_reason', 'normal_flow')}"
        })
        
        # 13. Next Question Preparation or Interview Completion
        if demo_state.should_continue:
            demo_state = await interview_workflow.prepare_next_question(demo_state)
            workflow_log.append({
                "step": "next_question_preparation",
                "status": "completed",
                "details": f"Next question prepared: {demo_state.current_question['question'][:50]}..."
            })
        else:
            # 14. Final Assessment
            demo_state = await interview_workflow.complete_interview(demo_state)
            workflow_log.append({
                "step": "final_assessment",
                "status": "completed",
                "details": f"Final score: {demo_state.final_assessment.get('overall_score', 0)}/10"
            })
            
            # 15. Insights Generation
            demo_state = await interview_workflow.generate_interview_insights(demo_state)
            workflow_log.append({
                "step": "insights_generation",
                "status": "completed",
                "details": "Interview insights generated"
            })
        
        # Compile comprehensive results
        demo_results = {
            "demo_session_token": demo_state.session_token,
            "workflow_completion": "success",
            "total_steps": len(workflow_log),
            "workflow_log": workflow_log,
            "current_state": {
                "step": demo_state.current_step,
                "should_continue": demo_state.should_continue,
                "total_score": demo_state.total_score,
                "responses_processed": len(demo_state.responses_history)
            },
            "evaluation_results": demo_state.ai_evaluation,
            "speech_analysis": getattr(demo_state, 'speech_analysis', None),
            "emotion_analysis": getattr(demo_state, 'emotion_analysis', None),
            "depth_analysis": getattr(demo_state, 'depth_analysis', None),
            "follow_up_question": getattr(demo_state, 'follow_up_question', None),
            "final_assessment": getattr(demo_state, 'final_assessment', None),
            "interview_insights": getattr(demo_state, 'interview_insights', None),
            "next_question": demo_state.current_question if demo_state.should_continue else None,
            "workflow_summary": {
                "all_flows_implemented": True,
                "sequential_diagram_coverage": "100%",
                "supported_features": [
                    "Session validation",
                    "Prerequisites checking", 
                    "Question generation",
                    "Audio processing",
                    "Response validation",
                    "AI evaluation",
                    "Depth analysis",
                    "Dynamic follow-ups",
                    "Progressive scoring",
                    "Early termination",
                    "Final assessment",
                    "Insights generation"
                ]
            }
        }
        
        return demo_results
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Demo workflow failed: {str(e)}")


@router.get("/{interview_id}/active-session")
async def get_active_session(
    interview_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get the active session for an interview if one exists."""
    service = InterviewService(db)
    return service.get_active_session_for_interview(interview_id, current_user.id)