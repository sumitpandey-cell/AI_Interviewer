"""
Simple workflow for AI interview orchestration
"""

import uuid
from typing import Dict, Any, List
from datetime import datetime

from ..interviews.schemas import LangGraphState
from .service import AIService

# Create an instance of AIService
ai_service = AIService()


class InterviewWorkflow:
    """Simple workflow for managing interview sessions."""
    
    def __init__(self):
        pass
    
    async def initialize_session(self, state: LangGraphState) -> LangGraphState:
        """Initialize the interview session."""
        state.current_step = "initialize_session"
        state.start_time = datetime.now()
        state.session_token = str(uuid.uuid4())
        state.current_question_index = 0
        state.responses_history = []
        state.total_score = 0.0
        state.should_continue = True
        
        return state
    
    async def generate_questions(self, state: LangGraphState) -> LangGraphState:
        """Generate interview questions using AI."""
        state.current_step = "generate_questions"
        
        try:
            questions = await ai_service.generate_interview_questions(
                position=state.position,
                interview_type=state.interview_type,
                difficulty=state.difficulty,
                num_questions=5
            )
            
            state.questions_generated = questions
            
        except Exception as e:
            state.error_message = f"Failed to generate questions: {str(e)}"
            state.should_continue = False
        
        return state

    async def validate_session(self, state: LangGraphState) -> LangGraphState:
        """Validate session state and user permissions."""
        state.current_step = "validate_session"
        
        if not state.session_token:
            state.error_message = "Invalid session token"
            state.should_continue = False
            return state
        
        if not state.user_id:
            state.error_message = "User not authenticated"
            state.should_continue = False
            return state
        
        # Additional validation logic here
        state.session_valid = True
        return state

    async def check_interview_prerequisites(self, state: LangGraphState) -> LangGraphState:
        """Check if all prerequisites for interview are met."""
        state.current_step = "check_prerequisites"
        
        prerequisites = {
            "questions_generated": bool(state.questions_generated),
            "user_authenticated": bool(state.user_id),
            "interview_configured": bool(state.position and state.interview_type),
            "session_initialized": bool(state.session_token)
        }
        
        if not all(prerequisites.values()):
            state.error_message = f"Prerequisites not met: {prerequisites}"
            state.should_continue = False
        
        return state
    
    async def present_question(self, state: LangGraphState) -> LangGraphState:
        """Present the current question to the user."""
        state.current_step = "present_question"
        
        if state.current_question_index < len(state.questions_generated):
            current_question = state.questions_generated[state.current_question_index]
            state.current_question = current_question
        else:
            # No more questions, end interview
            state.should_continue = False
        
        return state
    
    async def process_audio(self, state: LangGraphState) -> LangGraphState:
        """Process audio response and convert to text."""
        state.current_step = "process_audio"
        
        try:
            # Process audio data if available
            if state.audio_data:
                # Audio has already been processed by the audio_processing utility
                # The audio_data is now normalized to 16kHz mono WAV format
                # and the format is stored in state.audio_format
                
                # Get audio format from metadata or fallback to default
                audio_format = (
                    state.audio_metadata.get("detected_format") 
                    if hasattr(state, "audio_metadata") and state.audio_metadata
                    else (state.audio_format or "wav")
                )
                
                # Transcribe normalized audio data
                transcript = await ai_service.transcribe_audio_data(
                    audio_data=state.audio_data,
                    audio_format=audio_format
                )
                state.user_response = transcript
                
                # Analyze speech quality using audio data
                speech_analysis = await ai_service.analyze_speech_quality_data(
                    audio_data=state.audio_data,
                    transcript=transcript,
                    audio_format=audio_format
                )
                state.speech_analysis = speech_analysis
                
                # Detect emotions from audio data
                emotion_analysis = await ai_service.detect_emotions_data(
                    audio_data=state.audio_data,
                    transcript=transcript,
                    audio_format=audio_format
                )
                state.emotion_analysis = emotion_analysis
                
                # Add processing metrics to the state
                if hasattr(state, "audio_metadata") and state.audio_metadata:
                    processing_metrics = {
                        "original_format": state.audio_metadata.get("detected_format", "unknown"),
                        "original_size": state.audio_metadata.get("original_size", 0),
                        "processed_size": state.audio_metadata.get("processed_size", 0),
                        "processing_success": state.audio_metadata.get("processing_success", False)
                    }
                    state.audio_processing_metrics = processing_metrics
        except Exception as e:
            state.error_message = f"Audio processing failed: {str(e)}"
            # Still preserve user response if available
            if not state.user_response and hasattr(state, "audio_metadata"):
                state.user_response = "[Audio processing failed. Please provide a text response.]"
        
        return state
    
    async def validate_response(self, state: LangGraphState) -> LangGraphState:
        """Validate user response before processing."""
        state.current_step = "validate_response"
        
        if not state.user_response or len(state.user_response.strip()) < 10:
            state.error_message = "Response too short or empty"
            state.should_continue = False
            return state
        
        # Additional response validation
        response_length = len(state.user_response.split())
        if response_length > 1000:  # Too long
            state.warning_message = "Response is quite long, consider being more concise"
        elif response_length < 5:  # Too short
            state.warning_message = "Response seems brief, consider providing more detail"
        
        return state

    async def analyze_response_depth(self, state: LangGraphState) -> LangGraphState:
        """Analyze the depth and quality of the response."""
        state.current_step = "analyze_response_depth"
        
        try:
            if state.current_question and state.user_response:
                # Technical depth analysis
                if state.interview_type == "technical":
                    depth_analysis = await ai_service.assess_technical_depth(
                        question=state.current_question["question"],
                        response=state.user_response,
                        expected_level=state.difficulty
                    )
                    state.depth_analysis = depth_analysis
                
                # Behavioral analysis
                elif state.interview_type == "behavioral":
                    behavioral_analysis = await ai_service.evaluate_behavioral_response(
                        question=state.current_question["question"],
                        response=state.user_response,
                        criteria=state.current_question.get("expected_points", [])
                    )
                    state.behavioral_analysis = behavioral_analysis
                    
        except Exception as e:
            state.error_message = f"Response analysis failed: {str(e)}"
        
        return state

    async def generate_dynamic_follow_up(self, state: LangGraphState) -> LangGraphState:
        """Generate follow-up questions based on response quality."""
        state.current_step = "generate_follow_up"
        
        try:
            if state.current_question and state.user_response:
                # Determine if follow-up is needed
                evaluation = state.ai_evaluation or {}
                score = evaluation.get("overall_score", 5)
                
                # Generate follow-up for low scores or incomplete answers
                if score < 6 or len(state.user_response.split()) < 20:
                    follow_up = await ai_service.generate_follow_up_question(
                        previous_question=state.current_question["question"],
                        user_response=state.user_response,
                        interview_context={
                            "position": state.position,
                            "interview_type": state.interview_type,
                            "current_score": score
                        }
                    )
                    state.follow_up_question = follow_up
                    
        except Exception as e:
            state.error_message = f"Follow-up generation failed: {str(e)}"
        
        return state

    async def calculate_progressive_score(self, state: LangGraphState) -> LangGraphState:
        """Calculate running score and adjust difficulty."""
        state.current_step = "calculate_score"
        
        if state.ai_evaluation:
            current_score = state.ai_evaluation.get("overall_score", 0)
            state.total_score += current_score
            
            # Calculate average score so far
            questions_answered = len(state.responses_history) + 1
            average_score = state.total_score / questions_answered
            
            # Adjust difficulty for remaining questions
            if average_score > 8 and state.difficulty != "hard":
                state.difficulty = "hard"
                state.adjustment_message = "Increasing difficulty due to strong performance"
            elif average_score < 4 and state.difficulty != "easy":
                state.difficulty = "easy"
                state.adjustment_message = "Reducing difficulty to maintain engagement"
                
            state.current_average_score = average_score
        
        return state

    async def check_termination_conditions(self, state: LangGraphState) -> LangGraphState:
        """Check if interview should terminate early."""
        state.current_step = "check_termination"
        
        # Check various termination conditions
        questions_answered = len(state.responses_history)
        
        # Early termination conditions
        if questions_answered >= 2:
            average_score = state.total_score / questions_answered if questions_answered > 0 else 0
            
            # Very poor performance
            if average_score < 3 and questions_answered >= 3:
                state.should_continue = False
                state.termination_reason = "early_termination_poor_performance"
                return state
            
            # Excellent performance - can conclude early
            if average_score > 9 and questions_answered >= 4:
                state.should_continue = False
                state.termination_reason = "early_termination_excellent_performance"
                return state
        
        # Time-based termination
        if state.start_time:
            elapsed_minutes = (datetime.now() - state.start_time).total_seconds() / 60
            max_duration = getattr(state, 'max_duration_minutes', 60)
            
            if elapsed_minutes > max_duration:
                state.should_continue = False
                state.termination_reason = "time_limit_reached"
                return state
        
        # Standard completion
        if state.current_question_index >= len(state.questions_generated):
            state.should_continue = False
            state.termination_reason = "all_questions_completed"
        
        return state

    async def prepare_next_question(self, state: LangGraphState) -> LangGraphState:
        """Prepare the next question or follow-up."""
        state.current_step = "prepare_next_question"
        
        # If there's a follow-up question, use it
        if hasattr(state, 'follow_up_question') and state.follow_up_question:
            state.current_question = state.follow_up_question
            state.is_follow_up = True
            # Don't increment question index for follow-ups
        else:
            # Move to next regular question
            state.current_question_index += 1
            state.is_follow_up = False
            
            if state.current_question_index < len(state.questions_generated):
                state.current_question = state.questions_generated[state.current_question_index]
            else:
                state.should_continue = False
        
        # Clear follow-up for next iteration
        if hasattr(state, 'follow_up_question'):
            delattr(state, 'follow_up_question')
        
        return state
    
    async def complete_interview(self, state: LangGraphState) -> LangGraphState:
        """Complete the interview and generate final results."""
        state.current_step = "complete_interview"
        
        try:
            # Generate comprehensive final assessment
            interview_data = {
                "responses_history": state.responses_history,
                "total_score": state.total_score,
                "interview_type": state.interview_type,
                "position": state.position,
                "start_time": state.start_time,
                "end_time": datetime.now(),
                "termination_reason": getattr(state, 'termination_reason', 'completed_normally')
            }
            
            final_assessment = await ai_service.generate_final_assessment(interview_data)
            state.final_assessment = final_assessment
            
            # Calculate interview duration
            if state.start_time:
                duration = datetime.now() - state.start_time
                state.interview_duration = duration.total_seconds() / 60  # in minutes
            
            # Generate interview report
            state.interview_report = {
                "summary": final_assessment,
                "session_details": {
                    "session_token": state.session_token,
                    "questions_presented": len(state.questions_generated),
                    "questions_answered": len(state.responses_history),
                    "follow_ups_asked": len([r for r in state.responses_history if r.get("is_follow_up", False)]),
                    "duration_minutes": getattr(state, 'interview_duration', 0),
                    "termination_reason": getattr(state, 'termination_reason', 'completed_normally')
                },
                "performance_metrics": final_assessment.get("category_scores", {}),
                "recommendations": final_assessment.get("areas_for_improvement", []),
                "next_steps": self._generate_next_steps(final_assessment)
            }
            
        except Exception as e:
            state.error_message = f"Failed to complete interview assessment: {str(e)}"
            # Provide basic completion even if assessment fails
            state.final_assessment = {
                "overall_score": state.total_score / len(state.responses_history) if state.responses_history else 0,
                "recommendation": "Assessment incomplete due to error",
                "error": str(e)
            }
        
        state.should_continue = False
        state.completed_at = datetime.now()
        
        return state
    
    def _generate_next_steps(self, assessment: Dict[str, Any]) -> List[str]:
        """Generate next steps based on interview performance."""
        score = assessment.get("overall_score", 0)
        recommendation = assessment.get("recommendation", "")
        
        if score >= 8:
            return [
                "Proceed to final interview round",
                "Check references",
                "Prepare offer details",
                "Schedule culture fit interview"
            ]
        elif score >= 6:
            return [
                "Consider for next interview round",
                "Focus on areas needing improvement",
                "Conduct technical deep-dive if needed",
                "Get second interviewer opinion"
            ]
        else:
            return [
                "Provide constructive feedback",
                "Suggest areas for improvement", 
                "Consider for junior roles if applicable",
                "Thank candidate for their time"
            ]

    async def generate_interview_insights(self, state: LangGraphState) -> LangGraphState:
        """Generate insights about the interview process."""
        state.current_step = "generate_insights"
        
        insights = {
            "question_effectiveness": self._analyze_question_effectiveness(state),
            "candidate_patterns": self._analyze_candidate_patterns(state),
            "interview_flow": self._analyze_interview_flow(state),
            "recommendations_for_improvement": self._generate_process_improvements(state)
        }
        
        state.interview_insights = insights
        return state
    
    def _analyze_question_effectiveness(self, state: LangGraphState) -> Dict[str, Any]:
        """Analyze which questions were most effective."""
        effectiveness = {}
        
        for i, response in enumerate(state.responses_history):
            question = response.get("question", {})
            evaluation = response.get("evaluation", {})
            
            effectiveness[f"question_{i+1}"] = {
                "question_type": question.get("type", "unknown"),
                "response_quality": evaluation.get("overall_score", 0),
                "response_length": len(response.get("user_response", "").split()),
                "time_to_answer": response.get("response_time", 0)
            }
        
        return effectiveness
    
    def _analyze_candidate_patterns(self, state: LangGraphState) -> Dict[str, Any]:
        """Analyze patterns in candidate responses."""
        response_scores = [r.get("evaluation", {}).get("overall_score", 0) for r in state.responses_history]
        
        return {
            "performance_trend": "improving" if len(response_scores) > 1 and response_scores[-1] > response_scores[0] else "stable",
            "consistency": max(response_scores) - min(response_scores) if response_scores else 0,
            "best_category": self._find_best_performing_category(state),
            "communication_style": getattr(state, 'communication_style', 'not_analyzed')
        }
    
    def _analyze_interview_flow(self, state: LangGraphState) -> Dict[str, Any]:
        """Analyze the flow and pacing of the interview."""
        return {
            "total_duration": getattr(state, 'interview_duration', 0),
            "questions_per_minute": len(state.responses_history) / (getattr(state, 'interview_duration', 1) or 1),
            "follow_up_ratio": len([r for r in state.responses_history if r.get("is_follow_up", False)]) / len(state.responses_history) if state.responses_history else 0,
            "difficulty_adjustments": getattr(state, 'difficulty_adjustments', 0)
        }
    
    def _generate_process_improvements(self, state: LangGraphState) -> List[str]:
        """Generate suggestions for improving the interview process."""
        improvements = []
        
        if getattr(state, 'interview_duration', 0) > 60:
            improvements.append("Consider shortening interview duration")
        
        if len(state.responses_history) < 3:
            improvements.append("Consider asking more questions for better assessment")
        
        avg_score = state.total_score / len(state.responses_history) if state.responses_history else 0
        if avg_score < 5:
            improvements.append("Consider adjusting question difficulty or providing more guidance")
        
        return improvements
    
    def _find_best_performing_category(self, state: LangGraphState) -> str:
        """Find the category where candidate performed best."""
        category_scores = {}
        
        for response in state.responses_history:
            evaluation = response.get("evaluation", {})
            detailed_analysis = evaluation.get("detailed_analysis", {})
            
            for category, score in detailed_analysis.items():
                if category not in category_scores:
                    category_scores[category] = []
                category_scores[category].append(score)
        
        # Calculate average for each category
        category_averages = {
            category: sum(scores) / len(scores) 
            for category, scores in category_scores.items()
        }
        
        return max(category_averages.keys(), key=lambda k: category_averages[k]) if category_averages else "unknown"

    async def evaluate_response(self, state: LangGraphState) -> LangGraphState:
        """Evaluate the user's response to the current question."""
        state.current_step = "evaluate_response"
        
        try:
            if state.current_question and state.user_response:
                evaluation = await ai_service.evaluate_response(
                    question=state.current_question["question"],
                    user_response=state.user_response,
                    expected_points=state.current_question.get("expected_points"),
                    evaluation_criteria=state.current_question.get("evaluation_criteria")
                )
                
                state.ai_evaluation = evaluation
                
                # Store response in history
                response_record = {
                    "question": state.current_question,
                    "user_response": state.user_response,
                    "has_audio_data": state.audio_data is not None,
                    "evaluation": evaluation,
                    "timestamp": datetime.now().isoformat(),
                    "is_follow_up": getattr(state, 'is_follow_up', False),
                    "speech_analysis": getattr(state, 'speech_analysis', None),
                    "emotion_analysis": getattr(state, 'emotion_analysis', None)
                }
                
                state.responses_history.append(response_record)
                
        except Exception as e:
            state.error_message = f"Response evaluation failed: {str(e)}"
        
        return state

    async def generate_feedback(self, state: LangGraphState) -> LangGraphState:
        """Generate feedback for the user's response."""
        state.current_step = "generate_feedback"
        
        try:
            if state.ai_evaluation:
                # The feedback is already included in the evaluation
                state.feedback_generated = True
                
                # Optionally generate additional contextual feedback
                evaluation = state.ai_evaluation
                score = evaluation.get("overall_score", 0)
                
                if score >= 8:
                    state.encouragement_message = "Excellent response! Keep up the great work."
                elif score >= 6:
                    state.encouragement_message = "Good response! Consider the suggestions for improvement."
                elif score >= 4:
                    state.encouragement_message = "You're on the right track. Focus on the areas mentioned in the feedback."
                else:
                    state.encouragement_message = "Keep trying! Review the feedback and consider different approaches."
                    
        except Exception as e:
            state.error_message = f"Feedback generation failed: {str(e)}"
        
        return state

    async def determine_next_step(self, state: LangGraphState) -> LangGraphState:
        """Determine what the next step should be in the interview."""
        state.current_step = "determine_next_step"
        
        try:
            # Run all the analysis steps
            state = await self.validate_response(state)
            state = await self.analyze_response_depth(state)
            state = await self.generate_dynamic_follow_up(state)
            state = await self.calculate_progressive_score(state)
            state = await self.check_termination_conditions(state)
            
            # If we should continue, prepare the next question
            if state.should_continue and not state.error_message:
                state = await self.prepare_next_question(state)
            
        except Exception as e:
            state.error_message = f"Next step determination failed: {str(e)}"
            state.should_continue = False
        
        return state


# Global workflow instance
interview_workflow = InterviewWorkflow()
