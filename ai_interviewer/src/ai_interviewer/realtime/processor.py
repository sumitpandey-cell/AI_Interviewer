"""
Real-time interview processing with WebSocket integration
"""

import json
import logging
from typing import Dict, Any
from ..websocket.manager import websocket_manager
from ..external_apis.speech_service import SpeechService
from ..external_apis.storage_service import StorageService
from ..external_apis.video_analysis import VideoAnalysisService
from ..external_apis.notification_service import NotificationService

logger = logging.getLogger(__name__)

# Initialize external services
speech_service = SpeechService()
storage_service = StorageService()
video_service = VideoAnalysisService()
notification_service = NotificationService()


class RealTimeInterviewProcessor:
    """Real-time interview processor integrating all external APIs."""
    
    def __init__(self):
        self.active_sessions = {}
    
    async def process_audio_stream(self, session_token: str, audio_data: bytes, is_final: bool = False):
        """Process audio stream with real-time feedback."""
        try:
            # Send processing status via WebSocket
            await websocket_manager.send_audio_processing_status(
                session_token, 
                "processing", 
                {"message": "Processing audio stream..."}
            )
            
            # Store audio file
            audio_url = await storage_service.upload_audio_file(audio_data, session_token, "webm")
            
            # Analyze speech quality in real-time
            speech_analysis = await speech_service.analyze_speech_quality(audio_data)
            
            # Send speech analysis via WebSocket
            await websocket_manager.send_personal_message(session_token, {
                "type": "speech_analysis_update",
                "analysis": speech_analysis,
                "audio_url": audio_url
            })
            
            if is_final:
                # Perform comprehensive analysis for final audio
                emotion_analysis = await speech_service.analyze_speech_emotions(audio_data)
                pattern_analysis = await speech_service.detect_speech_patterns(audio_data)
                
                # Send final analysis
                await websocket_manager.send_personal_message(session_token, {
                    "type": "final_speech_analysis",
                    "emotion_analysis": emotion_analysis,
                    "pattern_analysis": pattern_analysis
                })
            
            return {
                "audio_url": audio_url,
                "speech_analysis": speech_analysis,
                "status": "processed"
            }
            
        except Exception as e:
            logger.error(f"Audio stream processing failed: {e}")
            await websocket_manager.send_error(session_token, "audio_processing_error", str(e))
            return {"error": str(e)}
    
    async def process_video_stream(self, session_token: str, video_data: bytes):
        """Process video stream for facial analysis."""
        try:
            # Send processing status
            await websocket_manager.send_personal_message(session_token, {
                "type": "video_processing",
                "status": "analyzing",
                "message": "Analyzing facial expressions and body language..."
            })
            
            # Store video file
            video_url = await storage_service.upload_video_file(video_data, session_token, "webm")
            
            # Perform video analysis
            facial_emotions = await video_service.analyze_facial_emotions(video_data)
            eye_contact = await video_service.analyze_eye_contact(video_data)
            body_language = await video_service.analyze_body_language(video_data)
            engagement = await video_service.analyze_engagement_level(video_data)
            
            # Send video analysis via WebSocket
            await websocket_manager.send_personal_message(session_token, {
                "type": "video_analysis_complete",
                "facial_emotions": facial_emotions,
                "eye_contact": eye_contact,
                "body_language": body_language,
                "engagement": engagement,
                "video_url": video_url
            })
            
            return {
                "video_url": video_url,
                "facial_emotions": facial_emotions,
                "eye_contact": eye_contact,
                "body_language": body_language,
                "engagement": engagement
            }
            
        except Exception as e:
            logger.error(f"Video processing failed: {e}")
            await websocket_manager.send_error(session_token, "video_processing_error", str(e))
            return {"error": str(e)}
    
    async def send_real_time_evaluation(self, session_token: str, evaluation_data: Dict[str, Any]):
        """Send real-time evaluation feedback."""
        try:
            # Process evaluation through AI
            enhanced_evaluation = await self._enhance_evaluation(evaluation_data)
            
            # Send via WebSocket
            await websocket_manager.send_evaluation_update(session_token, enhanced_evaluation)
            
            # Send encouragement message
            encouragement = self._generate_encouragement(enhanced_evaluation)
            await websocket_manager.send_personal_message(session_token, {
                "type": "encouragement",
                "message": encouragement
            })
            
        except Exception as e:
            logger.error(f"Real-time evaluation failed: {e}")
            await websocket_manager.send_error(session_token, "evaluation_error", str(e))
    
    async def handle_interview_completion(self, session_token: str, final_results: Dict[str, Any]):
        """Handle interview completion with notifications."""
        try:
            # Send completion status via WebSocket
            await websocket_manager.send_interview_status(session_token, "completed", final_results)
            
            # Send email notification
            user_email = final_results.get("user_email")
            if user_email:
                await notification_service.send_interview_completion(user_email, final_results)
            
            # Generate comprehensive report
            comprehensive_report = await self._generate_comprehensive_report(session_token, final_results)
            
            # Send final report via WebSocket
            await websocket_manager.send_personal_message(session_token, {
                "type": "final_report",
                "report": comprehensive_report
            })
            
        except Exception as e:
            logger.error(f"Interview completion handling failed: {e}")
            await websocket_manager.send_error(session_token, "completion_error", str(e))
    
    async def handle_connection_recovery(self, session_token: str):
        """Handle WebSocket connection recovery."""
        try:
            # Restore session state
            session_data = await self._get_session_state(session_token)
            
            if session_data:
                await websocket_manager.send_personal_message(session_token, {
                    "type": "session_restored",
                    "current_question": session_data.get("current_question"),
                    "progress": session_data.get("progress"),
                    "status": "reconnected"
                })
            else:
                await websocket_manager.send_error(session_token, "session_not_found", "Session could not be restored")
                
        except Exception as e:
            logger.error(f"Connection recovery failed: {e}")
            await websocket_manager.send_error(session_token, "recovery_error", str(e))
    
    async def _enhance_evaluation(self, evaluation_data: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance evaluation with additional insights."""
        # Add real-time insights
        evaluation_data["timestamp"] = evaluation_data.get("timestamp", "")
        evaluation_data["real_time_feedback"] = True
        evaluation_data["confidence_score"] = evaluation_data.get("confidence_score", 0.8)
        return evaluation_data
    
    def _generate_encouragement(self, evaluation_data: Dict[str, Any]) -> str:
        """Generate encouraging message based on evaluation."""
        score = evaluation_data.get("overall_score", 0)
        
        if score >= 8:
            return "Excellent answer! You're demonstrating strong knowledge and communication skills."
        elif score >= 6:
            return "Good response! You're on the right track. Keep up the good work!"
        elif score >= 4:
            return "Nice effort! Consider elaborating more on your experience and examples."
        else:
            return "Thank you for your response. Take your time to think through the next question."
    
    async def _generate_comprehensive_report(self, session_token: str, final_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive interview report."""
        return {
            "session_summary": {
                "session_token": session_token,
                "duration": final_results.get("duration", "N/A"),
                "questions_answered": final_results.get("questions_answered", 0),
                "overall_score": final_results.get("overall_score", 0)
            },
            "performance_breakdown": final_results.get("performance_breakdown", {}),
            "strengths": final_results.get("strengths", []),
            "areas_for_improvement": final_results.get("areas_for_improvement", []),
            "recommendations": final_results.get("recommendations", []),
            "next_steps": "Our team will review your interview and contact you within 3-5 business days."
        }
    
    async def _get_session_state(self, session_token: str) -> Dict[str, Any]:
        """Get current session state for recovery."""
        # In real implementation, this would query the database
        return {
            "current_question": {"question": "Sample question for recovery"},
            "progress": {"questions_answered": 2, "total_questions": 5},
            "status": "in_progress"
        }


# Global processor instance
real_time_processor = RealTimeInterviewProcessor()
