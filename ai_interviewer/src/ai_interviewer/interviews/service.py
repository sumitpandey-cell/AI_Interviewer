"""
Interview business logic and LangGraph workflow integration
"""

import uuid
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from fastapi import HTTPException
from sqlalchemy.orm import Session

from . import schemas, models
from .schemas import LangGraphState
from ..ai.workflow import interview_workflow
from ..auth.models import User
from ..utilities import process_audio_data


def clean_workflow_state_for_db(workflow_state: Dict[str, Any]) -> Dict[str, Any]:
    """Clean workflow state by converting datetime objects to strings and removing non-serializable data for JSON storage."""
    
    # Fields that should not be stored in the database (binary data, temporary processing data)
    EXCLUDE_FIELDS = {'audio_data', 'video_data', 'temp_data'}
    
    def clean_value(value, key=None):
        # Skip excluded fields
        if key in EXCLUDE_FIELDS:
            return None
            
        if isinstance(value, datetime):
            return value.isoformat()
        elif isinstance(value, bytes):
            # Don't store raw bytes in JSON - return metadata instead
            return f"<binary_data:{len(value)}_bytes>" if value else None
        elif isinstance(value, str):
            # Check if the string might contain binary data and avoid UTF-8 issues
            try:
                # Test if string can be safely encoded/decoded
                value.encode('utf-8').decode('utf-8')
                return value
            except (UnicodeDecodeError, UnicodeEncodeError):
                # If there are encoding issues, return safe metadata
                return f"<encoded_string:{len(value)}_chars>"
        elif isinstance(value, dict):
            return {k: clean_value(v, k) for k, v in value.items() if k not in EXCLUDE_FIELDS}
        elif isinstance(value, list):
            return [clean_value(item) for item in value]
        else:
            return value
    
    cleaned = clean_value(workflow_state)
    # Ensure we always return a dict
    return cleaned if isinstance(cleaned, dict) else {}


class InterviewService:
    """Service for managing interviews and workflow."""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def create_interview(
        self, 
        interview_data: schemas.InterviewCreate, 
        user_id: int
    ) -> models.Interview:
        """Create a new interview."""
        db_interview = models.Interview(
            user_id=user_id,
            title=interview_data.title,
            description=interview_data.description,
            position=interview_data.position,
            company=interview_data.company,
            interview_type=interview_data.interview_type,
            duration_minutes=interview_data.duration_minutes,
            status="created"
        )
        
        self.db.add(db_interview)
        self.db.commit()
        self.db.refresh(db_interview)
        
        return db_interview
    
    def get_interview(self, interview_id: int, user_id: int) -> models.Interview:
        """Get an interview by ID."""
        interview = self.db.query(models.Interview).filter(
            models.Interview.id == interview_id,
            models.Interview.user_id == user_id
        ).first()
        
        if not interview:
            raise HTTPException(status_code=404, detail="Interview not found")
        
        return interview
    
    def get_user_interviews(self, user_id: int) -> List[models.Interview]:
        """Get all interviews for a user."""
        return self.db.query(models.Interview).filter(
            models.Interview.user_id == user_id
        ).all()
    
    async def start_interview(
        self,
        interview_id: int,
        user_id: int
    ) -> Dict[str, Any]:
        """Start an interview session using LangGraph workflow."""
        
        # Get the interview
        interview = self.get_interview(interview_id, user_id)
        # Check for existing active session if the interview is in_progress
        if interview.status == "in_progress":
            # Get the active session
            session = self.db.query(models.InterviewSession).filter(
                models.InterviewSession.interview_id == interview_id,
                models.InterviewSession.is_active == True
            ).order_by(models.InterviewSession.created_at.desc()).first()
            
            if session:
                # Return the existing session
                state_dict = session.workflow_state or {}
                return {
                    "session_token": session.session_token,
                    "first_question": state_dict.get("current_question"),
                    "workflow_state": state_dict,
                    "is_resumed": True
                }
        
        # Only allow starting new sessions for interviews in 'created' status
        if interview.status != "created":
            raise HTTPException(
                status_code=400,
                detail=f"Interview cannot be started. Current status: {interview.status}"
            )
        
        # Create session token
        session_token = str(uuid.uuid4())
        
        # Create interview session record
        session = models.InterviewSession(
            interview_id=interview_id,
            session_token=session_token,
            is_active=True,
            session_status="initialized",
            current_step="initialize_session"
        )
        
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        
        # Initialize LangGraph state
        initial_state = LangGraphState(
            interview_id=interview_id,
            session_token=session_token,
            current_step="initialize_session",
            user_id=user_id,
            interview_type=interview.interview_type,
            position=interview.position,
            difficulty="medium"  # Default difficulty
        )
        
        # Run initialization steps
        state = await interview_workflow.initialize_session(initial_state)
        state = await interview_workflow.generate_questions(state)
        state = await interview_workflow.present_question(state)
        
        # Update session with workflow state
        session.workflow_state = clean_workflow_state_for_db(state.model_dump())
        session.current_step = state.current_step
        session.session_status = "started"
        
        # Update interview status
        interview.status = "in_progress"
        interview.started_at = datetime.now()
        
        self.db.commit()
        
        return {
            "session_token": session_token,
            "first_question": state.current_question,
            "workflow_state": state
        }
    
    async def submit_response(
        self, 
        session_token: str,
        response_text: Optional[str] = None,
        audio_data: Optional[Union[bytes, str]] = None
    ) -> Dict[str, Any]:
        """Submit a response to the current question."""
        
        # Get session
        session = self.db.query(models.InterviewSession).filter(
            models.InterviewSession.session_token == session_token,
            models.InterviewSession.is_active == True
        ).first()
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found or inactive")
        
        # Get current state
        state_dict = session.workflow_state or {}
        state = LangGraphState(**state_dict)
        
        # Update state with user response
        state.user_response = response_text
        
        # Process audio data using the new robust audio processing
        if audio_data:
            try:
                # Use the new audio processor to handle both base64 strings and bytes
                processed_audio, audio_metadata = process_audio_data(audio_data)
                
                # Update state with processed audio and metadata
                state.audio_data = processed_audio
                state.audio_format = audio_metadata["detected_format"]
                state.audio_metadata = audio_metadata
            except ValueError as e:
                # Return informative error for invalid audio
                raise HTTPException(status_code=400, detail=f"Audio processing error: {str(e)}")
            except Exception as e:
                # Log more serious errors but continue with text
                print(f"⚠️ Audio processing error: {str(e)}")
                state.audio_data = None
                state.audio_metadata = {"error": str(e)}
        else:
            state.audio_data = None
            state.audio_metadata = None
        
        # Process the response through workflow
        if audio_data:
            state = await interview_workflow.process_audio(state)
        
        state = await interview_workflow.evaluate_response(state)
        state = await interview_workflow.generate_feedback(state)
        state = await interview_workflow.determine_next_step(state)
        
        # Check if we should continue or complete
        if state.should_continue and not state.error_message:
            state = await interview_workflow.present_question(state)
        else:
            state = await interview_workflow.complete_interview(state)
            
            # Update interview status
            interview = session.interview
            interview.status = "completed"
            interview.completed_at = datetime.now()
            interview.score = state.total_score
            
            # Close session
            session.is_active = False
            session.session_status = "completed"
        
        # Update session with new state
        session.workflow_state = clean_workflow_state_for_db(state.model_dump())
        session.current_step = state.current_step
        session.last_activity_at = datetime.now()
        
        self.db.commit()
        
        # Prepare response
        evaluation = state.ai_evaluation or {}
        next_question = state.current_question if state.should_continue else None
        
        return {
            "evaluation": {
                "score": evaluation.get("overall_score", 0),
                "feedback": evaluation.get("feedback", ""),
                "detailed_analysis": evaluation.get("detailed_analysis", {}),
                "improvement_suggestions": evaluation.get("improvements", [])
            },
            "next_question": next_question,
            "is_completed": not state.should_continue,
            "workflow_state": state
        }
    
    def get_session_status(self, session_token: str) -> Dict[str, Any]:
        """Get the current status of an interview session."""
        session = self.db.query(models.InterviewSession).filter(
            models.InterviewSession.session_token == session_token
        ).first()
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        state_dict = session.workflow_state or {}
        state = LangGraphState(**state_dict) if state_dict else None
        
        return {
            "session_token": session_token,
            "is_active": session.is_active,
            "session_status": session.session_status,
            "current_step": session.current_step,
            "current_question": state.current_question if state else None,
            "responses_count": len(state.responses_history) if state else 0,
            "total_score": state.total_score if state else 0.0,
            "created_at": session.created_at,
            "last_activity_at": session.last_activity_at
        }
    
    def get_interview_results(self, interview_id: int, user_id: int) -> Dict[str, Any]:
        """Get the final results of a completed interview."""
        interview = self.get_interview(interview_id, user_id)
        
        if interview.status != "completed":
            raise HTTPException(
                status_code=400, 
                detail="Interview is not completed yet"
            )
        
        # Get the final session state
        session = self.db.query(models.InterviewSession).filter(
            models.InterviewSession.interview_id == interview_id
        ).order_by(models.InterviewSession.created_at.desc()).first()
        
        state_dict = session.workflow_state if session else {}
        state = LangGraphState(**state_dict) if state_dict else None
        
        return {
            "interview_id": interview_id,
            "title": interview.title,
            "position": interview.position,
            "interview_type": interview.interview_type,
            "status": interview.status,
            "score": interview.score,
            "feedback": interview.feedback,
            "started_at": interview.started_at,
            "completed_at": interview.completed_at,
            "duration_minutes": interview.duration_minutes,
            "responses_history": state.responses_history if state else [],
            "total_questions": len(state.questions_generated) if state else 0,
            "questions_answered": len(state.responses_history) if state else 0
        }
    
    async def execute_complete_workflow(
        self, 
        session_token: str,
        response_text: Optional[str] = None,
        audio_data: Optional[Union[bytes, str]] = None,
        include_analysis: bool = True
    ) -> Dict[str, Any]:
        """Execute the complete interview workflow for a response."""
        
        # Get session
        session = self.db.query(models.InterviewSession).filter(
            models.InterviewSession.session_token == session_token,
            models.InterviewSession.is_active == True
        ).first()
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found or inactive")
        
        # Get current state
        state_dict = session.workflow_state or {}
        state = LangGraphState(**state_dict)
        
        # Update state with new response
        state.user_response = response_text
        
        # Handle audio data (could be raw bytes or base64 encoded)
        if audio_data:
            if isinstance(audio_data, str):
                # If it's a string, assume it's base64 encoded
                import base64
                try:
                    state.audio_data = base64.b64decode(audio_data)
                except Exception as e:
                    raise HTTPException(status_code=400, detail=f"Invalid base64 audio data: {str(e)}")
            else:
                # Raw bytes
                state.audio_data = audio_data
        else:
            state.audio_data = None
        
        try:
            # Execute full workflow sequence from sequential diagram
            
            # 1. Session Validation
            state = await interview_workflow.validate_session(state)
            if not state.should_continue:
                raise HTTPException(status_code=400, detail=state.error_message)
            
            # 2. Prerequisites Check
            state = await interview_workflow.check_interview_prerequisites(state)
            if not state.should_continue:
                raise HTTPException(status_code=400, detail=state.error_message)
            
            # 3. Audio Processing (if audio provided)
            if audio_data:
                state = await interview_workflow.process_audio(state)
            
            # 4. Response Validation
            state = await interview_workflow.validate_response(state)
            if not state.should_continue:
                # Still continue if it's just a warning
                if "warning" not in (state.error_message or "").lower():
                    raise HTTPException(status_code=400, detail=state.error_message)
            
            # 5. Response Evaluation
            state = await interview_workflow.evaluate_response(state)
            
            # 6. Response Depth Analysis
            if include_analysis:
                state = await interview_workflow.analyze_response_depth(state)
            
            # 7. Dynamic Follow-up Generation
            state = await interview_workflow.generate_dynamic_follow_up(state)
            
            # 8. Progressive Scoring
            state = await interview_workflow.calculate_progressive_score(state)
            
            # 9. Feedback Generation
            state = await interview_workflow.generate_feedback(state)
            
            # 10. Termination Check
            state = await interview_workflow.check_termination_conditions(state)
            
            # 11. Next Question Preparation or Interview Completion
            if state.should_continue and not state.error_message:
                state = await interview_workflow.prepare_next_question(state)
            else:
                # 12. Final Assessment and Report Generation
                state = await interview_workflow.complete_interview(state)
                
                # 13. Insights Generation
                if include_analysis:
                    state = await interview_workflow.generate_interview_insights(state)
                
                # Update interview status
                interview = session.interview
                interview.status = "completed"
                interview.completed_at = datetime.now()
                interview.score = state.total_score
                
                # Close session
                session.is_active = False
                session.session_status = "completed"
            
            # Update session with new state
            session.workflow_state = clean_workflow_state_for_db(state.model_dump())
            session.current_step = state.current_step
            session.last_activity_at = datetime.now()
            
            self.db.commit()
            
            # Return comprehensive result
            return self._build_complete_response(state)
            
        except Exception as e:
            # Rollback on error
            self.db.rollback()
            raise HTTPException(status_code=500, detail=f"Workflow execution failed: {str(e)}")
    
    def _build_complete_response(self, state: LangGraphState) -> Dict[str, Any]:
        """Build a comprehensive response from the workflow state."""
        return {
            "session_token": state.session_token,
            "evaluation": state.ai_evaluation or {},
            "speech_analysis": getattr(state, 'speech_analysis', None),
            "emotion_analysis": getattr(state, 'emotion_analysis', None),
            "depth_analysis": getattr(state, 'depth_analysis', None),
            "behavioral_analysis": getattr(state, 'behavioral_analysis', None),
            "follow_up_question": getattr(state, 'follow_up_question', None),
            "current_score": getattr(state, 'current_average_score', 0),
            "difficulty_adjustment": getattr(state, 'adjustment_message', None),
            "next_question": state.current_question if state.should_continue else None,
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
                "should_continue": state.should_continue,
                "error_message": state.error_message
            }
        }

    async def validate_session_prerequisites(self, session_token: str) -> Dict[str, Any]:
        """Validate session and check all prerequisites."""
        session = self.db.query(models.InterviewSession).filter(
            models.InterviewSession.session_token == session_token,
            models.InterviewSession.is_active == True
        ).first()
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found or inactive")
        
        # Get current state
        state_dict = session.workflow_state or {}
        state = LangGraphState(**state_dict)
        
        # Run validation workflow
        state = await interview_workflow.validate_session(state)
        state = await interview_workflow.check_interview_prerequisites(state)
        
        # Update session
        session.workflow_state = clean_workflow_state_for_db(state.model_dump())
        session.current_step = state.current_step
        self.db.commit()
        
        return {
            "session_token": session_token,
            "is_valid": getattr(state, 'session_valid', True) and state.should_continue,
            "prerequisites_met": not bool(state.error_message),
            "current_step": state.current_step,
            "error_message": state.error_message,
            "validation_details": {
                "session_valid": getattr(state, 'session_valid', False),
                "questions_available": len(state.questions_generated) if state.questions_generated else 0,
                "user_authenticated": bool(state.user_id),
                "interview_configured": bool(state.position and state.interview_type)
            }
        }

    async def get_comprehensive_analysis(self, session_token: str) -> Dict[str, Any]:
        """Get comprehensive analysis of interview session."""
        session = self.db.query(models.InterviewSession).filter(
            models.InterviewSession.session_token == session_token
        ).first()
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Get current state
        state_dict = session.workflow_state or {}
        state = LangGraphState(**state_dict)
        
        # Calculate performance metrics
        response_scores = [
            r.get("evaluation", {}).get("overall_score", 0) 
            for r in state.responses_history
        ]
        avg_score = sum(response_scores) / len(response_scores) if response_scores else 0
        
        # Determine performance trend
        performance_trend = "stable"
        if len(response_scores) > 1:
            recent_scores = response_scores[-3:]  # Last 3 responses
            early_scores = response_scores[:3]   # First 3 responses
            
            if len(recent_scores) >= 2 and len(early_scores) >= 2:
                recent_avg = sum(recent_scores) / len(recent_scores)
                early_avg = sum(early_scores) / len(early_scores)
                
                if recent_avg > early_avg + 1:
                    performance_trend = "improving"
                elif recent_avg < early_avg - 1:
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
                "current_difficulty": state.difficulty,
                "score_distribution": {
                    "excellent": len([s for s in response_scores if s >= 8]),
                    "good": len([s for s in response_scores if 6 <= s < 8]),
                    "average": len([s for s in response_scores if 4 <= s < 6]),
                    "poor": len([s for s in response_scores if s < 4])
                }
            },
            "response_history": [
                {
                    "question_type": r.get("question", {}).get("type", "unknown"),
                    "question_text": r.get("question", {}).get("question", "")[:100] + "...",
                    "score": r.get("evaluation", {}).get("overall_score", 0),
                    "timestamp": r.get("timestamp"),
                    "is_follow_up": r.get("is_follow_up", False),
                    "response_length": len(r.get("user_response", "").split())
                }
                for r in state.responses_history
            ],
            "speech_quality_metrics": [
                {
                    "clarity_score": r.get("speech_analysis", {}).get("clarity_score", 0),
                    "pace_score": r.get("speech_analysis", {}).get("pace_score", 0),
                    "confidence_score": r.get("speech_analysis", {}).get("confidence_score", 0),
                    "overall_speech_score": r.get("speech_analysis", {}).get("overall_speech_score", 0)
                }
                for r in state.responses_history
                if r.get("speech_analysis")
            ],
            "emotion_patterns": [
                {
                    "primary_emotion": r.get("emotion_analysis", {}).get("primary_emotion", "unknown"),
                    "confidence": r.get("emotion_analysis", {}).get("emotion_scores", {}).get("confidence", 0),
                    "stress": r.get("emotion_analysis", {}).get("emotion_scores", {}).get("stress", 0),
                    "enthusiasm": r.get("emotion_analysis", {}).get("emotion_scores", {}).get("enthusiasm", 0)
                }
                for r in state.responses_history
                if r.get("emotion_analysis")
            ],
            "insights": getattr(state, 'interview_insights', None)
        }

    async def trigger_early_termination(
        self, 
        session_token: str, 
        reason: str,
        feedback: Optional[str] = None
    ) -> Dict[str, Any]:
        """Trigger early termination of interview."""
        session = self.db.query(models.InterviewSession).filter(
            models.InterviewSession.session_token == session_token,
            models.InterviewSession.is_active == True
        ).first()
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found or inactive")
        
        # Get current state
        state_dict = session.workflow_state or {}
        state = LangGraphState(**state_dict)
        
        # Set termination
        state.should_continue = False
        state.termination_reason = f"manual_termination_{reason}"
        if feedback:
            state.manual_feedback = feedback
        
        # Complete interview with early termination
        state = await interview_workflow.complete_interview(state)
        state = await interview_workflow.generate_interview_insights(state)
        
        # Update database
        interview = session.interview
        interview.status = "completed"
        interview.completed_at = datetime.now()
        interview.score = state.total_score
        interview.feedback = feedback
        
        session.is_active = False
        session.session_status = "completed"
        session.workflow_state = clean_workflow_state_for_db(state.model_dump())
        
        self.db.commit()
        
        return {
            "session_token": session_token,
            "message": "Interview terminated successfully",
            "termination_reason": state.termination_reason,
            "final_assessment": getattr(state, 'final_assessment', None),
            "interview_report": getattr(state, 'interview_report', None),
            "insights": getattr(state, 'interview_insights', None)
        }
    
    def get_active_session_for_interview(self, interview_id: int, user_id: int) -> Dict[str, Any]:
        """Get the active session for an interview, if one exists."""
        interview = self.get_interview(interview_id, user_id)
        
        # First check if interview is in progress
        if interview.status != "in_progress":
            return {
                "has_active_session": False,
                "message": f"Interview is not in progress. Current status: {interview.status}"
            }
        
        # Get the most recent active session
        session = self.db.query(models.InterviewSession).filter(
            models.InterviewSession.interview_id == interview_id,
            models.InterviewSession.is_active == True
        ).order_by(models.InterviewSession.created_at.desc()).first()
        
        if not session:
            return {
                "has_active_session": False,
                "message": "No active session found for this interview"
            }
        
        state_dict = session.workflow_state or {}
        
        return {
            "has_active_session": True,
            "session_token": session.session_token,
            "current_question": state_dict.get("current_question"),
            "current_step": session.current_step,
            "session_status": session.session_status,
            "last_activity_at": session.last_activity_at
        }
        

# Legacy functions for backward compatibility
async def create_interview(interview: schemas.InterviewCreate, db: Session):
    """Legacy function for creating interviews."""
    service = InterviewService(db)
    # Note: This needs user_id, but legacy function doesn't have it
    # You'll need to update callers to use the new service
    raise NotImplementedError("Use InterviewService.create_interview instead")


async def process_interview(interview_id: int, topic: str, time_limit: float, db: Session):
    """Legacy function for processing interviews."""
    # This would need to be updated to use the new workflow
    raise NotImplementedError("Use InterviewService.start_interview instead")