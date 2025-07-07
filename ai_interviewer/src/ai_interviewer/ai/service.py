"""
AI processing logic for interview workflow
"""

import os
import json
from typing import Dict, List, Any, Optional
from .prompts import prompt_template

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

try:
    from google.cloud import speech_v1p1beta1 as speech
    from google.cloud import storage
    GOOGLE_CLOUD_AVAILABLE = True
except ImportError:
    speech = None
    storage = None
    GOOGLE_CLOUD_AVAILABLE = False

from ..config import settings


class AIService:
    """Main AI service for interview processing."""
    
    def __init__(self):
        self.llm = None
        self.speech_client = None
        self.storage_client = None
        self.initialize_services()
    
    def initialize_services(self):
        """Initialize AI services."""
        try:
            # Initialize LLM
            if settings.GOOGLE_API_KEY:
                self.llm = ChatGoogleGenerativeAI(
                    model="gemini-1.5-flash",
                    google_api_key=settings.GOOGLE_API_KEY,
                    temperature=0.7
                )
                print("✅ Google Generative AI initialized")
            else:
                print("⚠️ Google Generative AI not initialized - missing API key")
        except Exception as e:
            print(f"⚠️ Failed to initialize Google Generative AI: {e}")
            self.llm = None
        
        try:
            # Initialize Google Cloud Speech
            if GOOGLE_CLOUD_AVAILABLE and speech:
                # Check for credentials
                credentials_available = (
                    settings.GOOGLE_APPLICATION_CREDENTIALS or 
                    os.getenv("GOOGLE_APPLICATION_CREDENTIALS") or
                    os.getenv("GOOGLE_CLOUD_PROJECT")
                )
                
                if credentials_available:
                    # Set credentials environment variable if provided
                    if settings.GOOGLE_APPLICATION_CREDENTIALS:
                        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = settings.GOOGLE_APPLICATION_CREDENTIALS
                    
                    self.speech_client = speech.SpeechClient()
                    print("✅ Google Cloud Speech initialized")
                else:
                    print("⚠️ Failed to initialize Google Cloud Speech: Your default credentials were not found. To set up Application Default Credentials, see https://cloud.google.com/docs/authentication/external/set-up-adc for more information.")
                    self.speech_client = None
            else:
                print("⚠️ Google Cloud Speech not available - install google-cloud-speech")
                self.speech_client = None
        except Exception as e:
            print(f"⚠️ Failed to initialize Google Cloud Speech: {e}")
            self.speech_client = None
        
        # try:
        #     # Initialize Google Cloud Storage
        #     if GOOGLE_CLOUD_AVAILABLE and storage and (settings.GOOGLE_CLOUD_API_KEY or os.getenv("GOOGLE_APPLICATION_CREDENTIALS")):
        #         self.storage_client = storage.Client()
        #         print("✅ Google Cloud Storage initialized")
        #     else:
        #         print("⚠️ Google Cloud Storage not initialized - missing credentials")
        #         self.storage_client = None
        # except Exception as e:
        #     print(f"⚠️ Failed to initialize Google Cloud Storage: {e}")
        #     self.storage_client = None


    async def generate_interview_questions(
        self, 
        position: str, 
        interview_type: str = "technical",
        difficulty: str = "medium",
        company: Optional[str] = None,
        num_questions: int = 5
    ) -> List[Dict[str, Any]]:
        """Generate interview questions using AI."""
        
        # If LLM is not available, return fallback questions
        if not self.llm:
            return self._get_fallback_questions(position, interview_type, difficulty, num_questions)
        
        try:
            # Create context-aware prompt for question generation
            company_context = f" at {company}" if company else ""
            
            
            
            # Format the prompt
            formatted_prompt = prompt_template.format(
                num_questions=num_questions,
                interview_type=interview_type,
                position=position,
                company_context=company_context,
                difficulty=difficulty
            )
            
            # Setup JSON output parser
            json_parser = JsonOutputParser()
            
            # Create the chain
            chain = prompt_template | self.llm | json_parser
            
            # Generate questions using AI
            result = await chain.ainvoke({
                "num_questions": num_questions,
                "interview_type": interview_type,
                "position": position,
                "company_context": company_context,
                "difficulty": difficulty
            })
            
            # Validate and process the result
            if isinstance(result, list) and len(result) > 0:
                questions = []
                for i, q in enumerate(result[:num_questions]):
                    if isinstance(q, dict) and "question" in q:
                        # Ensure all required fields are present
                        question_obj = {
                            "question": q.get("question", f"Default question {i+1}"),
                            "type": q.get("type", interview_type),
                            "difficulty": difficulty,
                            "expected_points": q.get("expected_points", ["General response"]),
                            "evaluation_criteria": q.get("evaluation_criteria", {"overall": 1.0})
                        }
                        
                        # Validate evaluation criteria sum to 1.0
                        criteria_sum = sum(question_obj["evaluation_criteria"].values())
                        if abs(criteria_sum - 1.0) > 0.1:  # Allow small floating point errors
                            # Normalize criteria
                            question_obj["evaluation_criteria"] = {
                                k: v / criteria_sum for k, v in question_obj["evaluation_criteria"].items()
                            }
                        
                        questions.append(question_obj)
                
                if questions:
                    return questions
            
            # If AI generation failed, return fallback
            print("⚠️ AI generation returned invalid format, using fallback questions")
            return self._get_fallback_questions(position, interview_type, difficulty, num_questions)
            
        except Exception as e:
            print(f"⚠️ Error generating questions with AI: {e}")
            # Return fallback questions on error
            return self._get_fallback_questions(position, interview_type, difficulty, num_questions)
    
    def _get_fallback_questions(
        self, 
        position: str, 
        interview_type: str, 
        difficulty: str, 
        num_questions: int
    ) -> List[Dict[str, Any]]:
        """Generate fallback questions when AI is not available."""
        
        if interview_type == "technical":
            base_questions = [
                {
                    "question": f"Tell me about your experience with {position} development and the technologies you've worked with.",
                    "type": "experience",
                    "expected_points": ["Experience", "Technologies", "Projects", "Challenges"],
                    "evaluation_criteria": {"technical_knowledge": 0.6, "communication": 0.4}
                },
                {
                    "question": f"Describe a challenging {position} problem you solved. Walk me through your approach.",
                    "type": "problem_solving",
                    "expected_points": ["Problem description", "Solution approach", "Implementation", "Results"],
                    "evaluation_criteria": {"problem_solving": 0.7, "technical_depth": 0.3}
                },
                {
                    "question": f"How do you ensure code quality and maintainability in {position} projects?",
                    "type": "best_practices",
                    "expected_points": ["Code review", "Testing", "Documentation", "Standards"],
                    "evaluation_criteria": {"technical_knowledge": 0.5, "best_practices": 0.5}
                },
                {
                    "question": f"Explain how you would design a scalable system for a {position.lower()} application.",
                    "type": "system_design",
                    "expected_points": ["Architecture", "Scalability", "Performance", "Trade-offs"],
                    "evaluation_criteria": {"system_design": 0.8, "technical_depth": 0.2}
                },
                {
                    "question": f"How do you stay updated with the latest {position} technologies and trends?",
                    "type": "learning",
                    "expected_points": ["Learning resources", "Community involvement", "Experimentation"],
                    "evaluation_criteria": {"learning_mindset": 0.6, "technical_awareness": 0.4}
                }
            ]
        
        elif interview_type == "behavioral":
            base_questions = [
                {
                    "question": "Tell me about a time when you had to work with a difficult team member. How did you handle it?",
                    "type": "teamwork",
                    "expected_points": ["Situation", "Action", "Communication", "Result"],
                    "evaluation_criteria": {"teamwork": 0.5, "communication": 0.3, "conflict_resolution": 0.2}
                },
                {
                    "question": "Describe a project where you had to learn something new quickly. How did you approach it?",
                    "type": "adaptability",
                    "expected_points": ["Learning approach", "Resources used", "Timeline", "Outcome"],
                    "evaluation_criteria": {"adaptability": 0.6, "learning_ability": 0.4}
                },
                {
                    "question": "Tell me about a time when you had to make a difficult decision with limited information.",
                    "type": "decision_making",
                    "expected_points": ["Context", "Decision process", "Risk assessment", "Outcome"],
                    "evaluation_criteria": {"decision_making": 0.7, "analytical_thinking": 0.3}
                },
                {
                    "question": "Describe a situation where you had to lead a project or initiative. What was your approach?",
                    "type": "leadership",
                    "expected_points": ["Leadership style", "Planning", "Team motivation", "Results"],
                    "evaluation_criteria": {"leadership": 0.6, "project_management": 0.4}
                },
                {
                    "question": "Tell me about a time when you received criticism. How did you handle it?",
                    "type": "feedback",
                    "expected_points": ["Reception", "Processing", "Action taken", "Growth"],
                    "evaluation_criteria": {"emotional_intelligence": 0.5, "growth_mindset": 0.5}
                }
            ]
        
        else:  # mixed
            base_questions = [
                {
                    "question": f"Tell me about your experience with {position} development and how you've grown in this role.",
                    "type": "experience_growth",
                    "expected_points": ["Technical experience", "Career progression", "Learning", "Goals"],
                    "evaluation_criteria": {"technical_knowledge": 0.4, "career_growth": 0.3, "communication": 0.3}
                },
                {
                    "question": f"Describe a {position} project that didn't go as planned. How did you handle it?",
                    "type": "problem_resolution",
                    "expected_points": ["Problem identification", "Technical solutions", "Team dynamics", "Learning"],
                    "evaluation_criteria": {"problem_solving": 0.4, "adaptability": 0.3, "technical_skills": 0.3}
                },
                {
                    "question": f"How do you balance technical debt with feature development in {position} projects?",
                    "type": "technical_management",
                    "expected_points": ["Technical understanding", "Prioritization", "Communication", "Strategy"],
                    "evaluation_criteria": {"technical_knowledge": 0.5, "strategic_thinking": 0.3, "communication": 0.2}
                }
            ]
        
        # Adjust questions based on difficulty
        if difficulty == "easy":
            # Use simpler language and basic concepts
            for q in base_questions:
                q["question"] = q["question"].replace("challenging", "simple")
                q["question"] = q["question"].replace("complex", "basic")
        elif difficulty == "hard":
            # Add more complex scenarios
            for q in base_questions:
                if "system" in q["question"].lower():
                    q["question"] = q["question"].replace("scalable system", "highly scalable, distributed system")
        
        # Add difficulty and return requested number
        for q in base_questions:
            q["difficulty"] = difficulty
        
        return base_questions[:num_questions]

    async def evaluate_response(
        self, 
        question: str, 
        user_response: str,
        expected_points: Optional[List[str]] = None,
        evaluation_criteria: Optional[Dict[str, float]] = None
    ) -> Dict[str, Any]:
        """Evaluate a user's response to an interview question."""
        # Return mock evaluation for now
        return {
            "overall_score": 7.5,
            "feedback": "Good response! You demonstrated understanding of the topic. Consider providing more specific examples.",
            "detailed_analysis": {
                "technical_accuracy": 8,
                "communication": 7,
                "completeness": 7
            },
            "improvements": ["Provide more concrete examples", "Elaborate on specific technologies used"]
        }

    async def transcribe_audio(self, audio_url: str) -> str:
        """Transcribe audio from a URL using Google Cloud Speech-to-Text."""
        # Return mock transcription for now
        return f"[Mock transcription] This is a simulated transcription of the audio file at {audio_url}. The candidate spoke clearly about their experience and provided detailed examples."

    async def analyze_speech_quality(self, audio_url: str, transcript: str) -> Dict[str, Any]:
        """Analyze speech quality metrics from audio."""
        # In a real implementation, this would analyze audio characteristics
        return {
            "clarity_score": 8.5,
            "pace_score": 7.8,
            "volume_score": 8.0,
            "confidence_score": 7.5,
            "fluency_score": 8.2,
            "overall_speech_score": 8.0,
            "feedback": "Clear speech with good pace. Consider speaking with more confidence.",
            "recommendations": [
                "Maintain consistent volume",
                "Use more confident tone",
                "Good articulation overall"
            ]
        }

    async def detect_emotions(self, audio_url: str, transcript: str) -> Dict[str, Any]:
        """Detect emotions from audio and text."""
        # Mock emotion detection
        return {
            "primary_emotion": "confident",
            "emotion_scores": {
                "confidence": 0.75,
                "nervousness": 0.15,
                "enthusiasm": 0.65,
                "stress": 0.20
            },
            "emotional_stability": 8.0,
            "recommendations": [
                "Good emotional control",
                "Show more enthusiasm when discussing achievements"
            ]
        }

    async def generate_follow_up_question(
        self, 
        previous_question: str, 
        user_response: str,
        interview_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate contextual follow-up questions."""
        # Mock follow-up generation based on response
        follow_ups = [
            "Can you provide a specific example of that?",
            "How did you overcome the challenges you mentioned?",
            "What technologies did you use for that project?",
            "How would you approach this differently now?",
            "What did you learn from that experience?"
        ]
        
        return {
            "question": follow_ups[0],  # In real implementation, use AI to select best follow-up
            "type": "follow_up",
            "context": f"Following up on: {previous_question[:50]}...",
            "reasoning": "Seeking specific examples to validate claimed experience"
        }

    async def assess_technical_depth(
        self, 
        question: str, 
        response: str, 
        expected_level: str = "intermediate"
    ) -> Dict[str, Any]:
        """Assess the technical depth of a response."""
        return {
            "depth_score": 7.5,
            "technical_accuracy": 8.0,
            "complexity_level": "intermediate",
            "knowledge_gaps": ["Could elaborate on scalability considerations"],
            "strengths": ["Good understanding of core concepts", "Practical experience evident"],
            "suggestions": [
                "Provide more technical details",
                "Discuss trade-offs and alternatives"
            ]
        }

    async def evaluate_behavioral_response(
        self, 
        question: str, 
        response: str,
        criteria: List[str]
    ) -> Dict[str, Any]:
        """Evaluate behavioral interview responses using STAR method."""
        return {
            "star_analysis": {
                "situation": 8.0,
                "task": 7.5,
                "action": 8.5,
                "result": 7.0
            },
            "overall_score": 7.8,
            "competencies": {
                "leadership": 7.5,
                "problem_solving": 8.0,
                "communication": 8.5,
                "teamwork": 7.8
            },
            "feedback": "Good use of STAR method. Clearly described situation and actions taken.",
            "improvements": [
                "Quantify results more specifically",
                "Elaborate on lessons learned"
            ]
        }

    async def generate_final_assessment(
        self, 
        interview_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate comprehensive final interview assessment."""
        responses = interview_data.get("responses_history", [])
        
        # Calculate aggregate scores
        technical_scores = []
        behavioral_scores = []
        communication_scores = []
        
        for response in responses:
            eval_data = response.get("evaluation", {})
            if eval_data:
                technical_scores.append(eval_data.get("technical_accuracy", 5))
                behavioral_scores.append(eval_data.get("overall_score", 5))
                communication_scores.append(eval_data.get("communication", 5))
        
        avg_technical = sum(technical_scores) / len(technical_scores) if technical_scores else 5.0
        avg_behavioral = sum(behavioral_scores) / len(behavioral_scores) if behavioral_scores else 5.0
        avg_communication = sum(communication_scores) / len(communication_scores) if communication_scores else 5.0
        
        overall_score = (avg_technical * 0.4 + avg_behavioral * 0.4 + avg_communication * 0.2)
        
        # Determine recommendation
        if overall_score >= 8.0:
            recommendation = "Strong Hire"
        elif overall_score >= 7.0:
            recommendation = "Hire"
        elif overall_score >= 6.0:
            recommendation = "Weak Hire"
        elif overall_score >= 5.0:
            recommendation = "Weak No Hire"
        else:
            recommendation = "No Hire"
        
        return {
            "overall_score": round(overall_score, 1),
            "recommendation": recommendation,
            "category_scores": {
                "technical_skills": round(avg_technical, 1),
                "behavioral_competencies": round(avg_behavioral, 1),
                "communication_skills": round(avg_communication, 1)
            },
            "strengths": [
                "Demonstrated solid technical knowledge",
                "Good communication skills",
                "Relevant experience for the role"
            ],
            "areas_for_improvement": [
                "Could provide more specific examples",
                "Elaborate on technical decisions",
                "Show more enthusiasm"
            ],
            "detailed_feedback": "Candidate showed good overall competency with room for growth in specific areas.",
            "interview_stats": {
                "total_questions": len(responses),
                "questions_answered": len([r for r in responses if r.get("user_response")]),
                "average_response_quality": round(overall_score, 1)
            }
        }

    async def validate_audio_quality(self, audio_url: str) -> Dict[str, Any]:
        """Validate audio quality before processing."""
        # In a real implementation, this would analyze audio file characteristics
        return {
            "is_valid": True,
            "quality_score": 8.5,
            "duration_seconds": 45.0,
            "sample_rate": 44100,
            "format": "wav",
            "issues": [],
            "recommendations": ["Audio quality is good for processing"]
        }

    async def generate_contextual_questions(
        self, 
        interview_context: Dict[str, Any],
        response_history: List[Dict[str, Any]],
        difficulty_level: str = "medium"
    ) -> List[Dict[str, Any]]:
        """Generate contextual questions based on interview progress."""
        position = interview_context.get("position", "software engineer")
        interview_type = interview_context.get("interview_type", "technical")
        
        # Analyze response history to determine focus areas
        weak_areas = self._identify_weak_areas(response_history)
        strong_areas = self._identify_strong_areas(response_history)
        
        # Generate targeted questions
        questions = []
        
        if interview_type == "technical":
            if "problem_solving" in weak_areas:
                questions.append({
                    "question": f"Describe a complex {position} problem you solved and walk me through your approach.",
                    "type": "technical_problem_solving",
                    "difficulty": difficulty_level,
                    "focus_area": "problem_solving",
                    "expected_points": ["Problem identification", "Solution approach", "Implementation details", "Results"],
                    "evaluation_criteria": {"problem_solving": 0.7, "technical_depth": 0.3}
                })
            
            if "system_design" in weak_areas:
                questions.append({
                    "question": f"How would you design a scalable system for {position.lower()} applications?",
                    "type": "system_design",
                    "difficulty": difficulty_level,
                    "focus_area": "system_design",
                    "expected_points": ["Scalability", "Architecture", "Trade-offs", "Technology choices"],
                    "evaluation_criteria": {"system_design": 0.8, "technical_depth": 0.2}
                })
        
        elif interview_type == "behavioral":
            if "leadership" in weak_areas:
                questions.append({
                    "question": "Tell me about a time when you had to lead a team through a challenging project.",
                    "type": "behavioral_leadership",
                    "difficulty": difficulty_level,
                    "focus_area": "leadership",
                    "expected_points": ["Situation", "Task", "Action", "Result"],
                    "evaluation_criteria": {"leadership": 0.6, "communication": 0.4}
                })
        
        return questions

    def _identify_weak_areas(self, response_history: List[Dict[str, Any]]) -> List[str]:
        """Identify areas where candidate is performing poorly."""
        weak_areas = []
        
        category_scores = {}
        for response in response_history:
            evaluation = response.get("evaluation", {})
            detailed_analysis = evaluation.get("detailed_analysis", {})
            
            for category, score in detailed_analysis.items():
                if category not in category_scores:
                    category_scores[category] = []
                category_scores[category].append(score)
        
        # Find categories with average score below 6
        for category, scores in category_scores.items():
            avg_score = sum(scores) / len(scores)
            if avg_score < 6:
                weak_areas.append(category)
        
        return weak_areas

    def _identify_strong_areas(self, response_history: List[Dict[str, Any]]) -> List[str]:
        """Identify areas where candidate is performing well."""
        strong_areas = []
        
        category_scores = {}
        for response in response_history:
            evaluation = response.get("evaluation", {})
            detailed_analysis = evaluation.get("detailed_analysis", {})
            
            for category, score in detailed_analysis.items():
                if category not in category_scores:
                    category_scores[category] = []
                category_scores[category].append(score)
        
        # Find categories with average score above 7.5
        for category, scores in category_scores.items():
            avg_score = sum(scores) / len(scores)
            if avg_score > 7.5:
                strong_areas.append(category)
        
        return strong_areas

    async def analyze_interview_progression(
        self, 
        response_history: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze how the interview is progressing."""
        if not response_history:
            return {"progression": "just_started", "confidence": "unknown"}
        
        scores = [r.get("evaluation", {}).get("overall_score", 0) for r in response_history]
        
        # Calculate trend
        if len(scores) >= 3:
            recent_avg = sum(scores[-2:]) / 2
            early_avg = sum(scores[:2]) / 2
            
            if recent_avg > early_avg + 1:
                trend = "improving"
            elif recent_avg < early_avg - 1:
                trend = "declining"
            else:
                trend = "stable"
        else:
            trend = "insufficient_data"
        
        # Calculate consistency
        if len(scores) > 1:
            consistency = 10 - (max(scores) - min(scores))
        else:
            consistency = 5
        
        # Determine overall confidence
        avg_score = sum(scores) / len(scores)
        if avg_score >= 8:
            confidence_level = "high"
        elif avg_score >= 6:
            confidence_level = "medium"
        else:
            confidence_level = "low"
        
        return {
            "progression": trend,
            "confidence": confidence_level,
            "consistency_score": consistency,
            "average_performance": avg_score,
            "total_responses": len(response_history),
            "performance_summary": {
                "excellent_responses": len([s for s in scores if s >= 8]),
                "good_responses": len([s for s in scores if 6 <= s < 8]),
                "poor_responses": len([s for s in scores if s < 6])
            }
        }

    async def determine_optimal_difficulty(
        self, 
        response_history: List[Dict[str, Any]],
        current_difficulty: str
    ) -> str:
        """Determine optimal difficulty for next questions."""
        if not response_history:
            return current_difficulty
        
        recent_scores = [
            r.get("evaluation", {}).get("overall_score", 0) 
            for r in response_history[-3:]  # Last 3 responses
        ]
        
        avg_recent = sum(recent_scores) / len(recent_scores)
        
        # Difficulty adjustment logic
        if avg_recent >= 8.5 and current_difficulty != "hard":
            return "hard"
        elif avg_recent <= 4.0 and current_difficulty != "easy":
            return "easy"
        elif 5.5 <= avg_recent <= 7.5 and current_difficulty != "medium":
            return "medium"
        
        return current_difficulty

    async def generate_personalized_feedback(
        self, 
        response: str,
        evaluation: Dict[str, Any],
        candidate_profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate personalized feedback based on candidate profile."""
        score = evaluation.get("overall_score", 0)
        detailed_analysis = evaluation.get("detailed_analysis", {})
        
        # Customize feedback based on experience level
        experience_level = candidate_profile.get("experience_level", "intermediate")
        
        feedback_tone = "encouraging" if score >= 6 else "constructive"
        
        personalized_feedback = {
            "primary_feedback": evaluation.get("feedback", ""),
            "tone": feedback_tone,
            "specific_improvements": [],
            "encouragement": "",
            "next_focus_areas": []
        }
        
        # Add experience-specific suggestions
        if experience_level == "junior":
            if score >= 6:
                personalized_feedback["encouragement"] = "Great job! You're showing strong foundational knowledge."
            else:
                personalized_feedback["encouragement"] = "Keep learning! Everyone starts somewhere."
                
        elif experience_level == "senior":
            if score < 7:
                personalized_feedback["specific_improvements"].append(
                    "Consider providing more strategic insights given your experience level"
                )
        
        return personalized_feedback

    async def predict_interview_outcome(
        self, 
        response_history: List[Dict[str, Any]],
        remaining_questions: int
    ) -> Dict[str, Any]:
        """Predict likely interview outcome based on current performance."""
        if not response_history:
            return {"prediction": "insufficient_data", "confidence": 0}
        
        scores = [r.get("evaluation", {}).get("overall_score", 0) for r in response_history]
        avg_score = sum(scores) / len(scores)
        
        # Calculate trend weight
        if len(scores) >= 2:
            trend_weight = scores[-1] - scores[0] if len(scores) == 2 else (scores[-1] - scores[-2])
        else:
            trend_weight = 0
        
        # Predict final score
        predicted_score = avg_score + (trend_weight * remaining_questions * 0.1)
        predicted_score = max(0, min(10, predicted_score))  # Clamp between 0-10
        
        # Determine recommendation
        if predicted_score >= 7.5:
            prediction = "likely_hire"
            confidence = 0.8
        elif predicted_score >= 6.0:
            prediction = "borderline"
            confidence = 0.6
        else:
            prediction = "likely_no_hire"
            confidence = 0.7
        
        return {
            "prediction": prediction,
            "predicted_final_score": round(predicted_score, 1),
            "confidence": confidence,
            "current_average": round(avg_score, 1),
            "trend": "positive" if trend_weight > 0 else "negative" if trend_weight < 0 else "stable",
            "responses_analyzed": len(scores)
        }

    # Direct Audio Data Processing Methods (for real-time streaming)
    
    async def transcribe_audio_data(self, audio_data: bytes, audio_format: str = "wav") -> str:
        """Transcribe audio data directly using Google Cloud Speech-to-Text."""
        try:
            if not self.speech_client:
                return "[Audio transcription not available - please type your response]"
            
            # Audio format should already be normalized to 16kHz mono WAV by the audio_processing utility
            # But we'll still handle different formats for robustness
            
            # Configure recognition based on audio format
            if audio_format.lower() in ["webm", "webm-opus"]:
                encoding = speech.RecognitionConfig.AudioEncoding.WEBM_OPUS
                sample_rate = 48000
            elif audio_format.lower() == "mp3":
                encoding = speech.RecognitionConfig.AudioEncoding.MP3
                sample_rate = 16000
            elif audio_format.lower() == "wav":
                encoding = speech.RecognitionConfig.AudioEncoding.LINEAR16
                sample_rate = 16000  # Our audio_processing utility normalizes to 16kHz
            elif audio_format.lower() == "ogg":
                encoding = speech.RecognitionConfig.AudioEncoding.OGG_OPUS
                sample_rate = 48000
            else:
                # Default to LINEAR16 (WAV) since our audio processor normalizes to WAV
                encoding = speech.RecognitionConfig.AudioEncoding.LINEAR16
                sample_rate = 16000
            
            # Create audio object from bytes
            audio = speech.RecognitionAudio(content=audio_data)
            
            # Configure recognition
            config = speech.RecognitionConfig(
                encoding=encoding,
                sample_rate_hertz=sample_rate,
                language_code="en-US",
                enable_automatic_punctuation=True,
                enable_word_time_offsets=True,
                enable_word_confidence=True,
                model="latest_long"  # Better for interview responses
            )
            
            # Perform transcription
            response = self.speech_client.recognize(config=config, audio=audio)
            
            # Extract transcript with confidence
            transcript_parts = []
            total_confidence = 0
            part_count = 0
            
            for result in response.results:
                alternative = result.alternatives[0]
                transcript_parts.append(alternative.transcript)
                total_confidence += alternative.confidence
                part_count += 1
            
            transcript = " ".join(transcript_parts).strip()
            avg_confidence = total_confidence / part_count if part_count > 0 else 0
            
            # Return transcript or fallback message
            if transcript and avg_confidence > 0.5:
                return transcript
            else:
                return "[Audio unclear - please speak more clearly or type your response]"
                
        except Exception as e:
            print(f"⚠️ Audio transcription error: {e}")
            return "[Audio transcription failed - please type your response]"

    async def analyze_speech_quality_data(self, audio_data: bytes, transcript: str, audio_format: str = "webm") -> Dict[str, Any]:
        """Analyze speech quality from audio data."""
        try:
            # Basic analysis using transcript and audio metadata
            words = transcript.split()
            
            # Estimate speech characteristics
            word_count = len(words)
            estimated_duration = len(audio_data) / (16000 * 2)  # Rough estimate
            speech_rate = (word_count / estimated_duration * 60) if estimated_duration > 0 else 120
            
            # Calculate quality metrics
            clarity_score = min(10, len(transcript) / 10)  # Based on transcript length
            pace_score = 10 - abs(speech_rate - 150) / 20  # Optimal ~150 WPM
            pace_score = max(1, min(10, pace_score))
            
            # Audio format quality assessment
            format_quality = {
                "webm": 8.5,
                "mp3": 7.5,
                "wav": 9.0,
                "ogg": 8.0
            }.get(audio_format.lower(), 7.0)
            
            # Fluency indicators
            filler_words = ["um", "uh", "er", "like", "you know", "actually"]
            filler_count = sum(1 for word in words if word.lower() in filler_words)
            fluency_score = max(1, 10 - (filler_count * 2))
            
            overall_score = (clarity_score + pace_score + format_quality + fluency_score) / 4
            
            return {
                "clarity_score": round(clarity_score, 1),
                "pace_score": round(pace_score, 1),
                "volume_score": format_quality,  # Proxy based on format
                "confidence_score": round(fluency_score, 1),
                "fluency_score": round(fluency_score, 1),
                "overall_speech_score": round(overall_score, 1),
                "metadata": {
                    "word_count": word_count,
                    "estimated_duration": round(estimated_duration, 2),
                    "speech_rate_wpm": round(speech_rate, 0),
                    "audio_format": audio_format,
                    "filler_words_count": filler_count
                },
                "feedback": self._generate_speech_feedback(overall_score, speech_rate, filler_count),
                "recommendations": self._generate_speech_recommendations(clarity_score, pace_score, fluency_score)
            }
            
        except Exception as e:
            print(f"⚠️ Speech quality analysis error: {e}")
            return {
                "error": f"Speech analysis failed: {e}",
                "overall_speech_score": 5.0,
                "feedback": "Unable to analyze speech quality"
            }

    async def detect_emotions_data(self, audio_data: bytes, transcript: str, audio_format: str = "webm") -> Dict[str, Any]:
        """Detect emotions from audio data and transcript."""
        try:
            # Text-based emotion analysis
            words = transcript.lower().split()
            
            # Emotion keywords
            emotion_keywords = {
                "confidence": ["confident", "sure", "certain", "definitely", "absolutely"],
                "enthusiasm": ["excited", "great", "amazing", "fantastic", "love", "enjoy"],
                "nervousness": ["um", "uh", "nervous", "worried", "uncertain", "maybe"],
                "stress": ["difficult", "hard", "challenging", "struggle", "pressure"],
                "positivity": ["good", "excellent", "wonderful", "positive", "happy", "successful"]
            }
            
            # Calculate emotion scores
            emotion_scores = {}
            for emotion, keywords in emotion_keywords.items():
                score = sum(1 for word in words if word in keywords) / len(words) if words else 0
                emotion_scores[emotion] = min(1.0, score * 10)  # Normalize to 0-1
            
            # Determine primary emotion
            primary_emotion = max(emotion_scores.keys(), key=lambda k: emotion_scores[k])
            primary_score = emotion_scores[primary_emotion]
            
            # Audio-based indicators (simulated based on format and length)
            audio_length = len(audio_data)
            volume_variation = min(1.0, audio_length / 100000)  # Proxy for volume variation
            
            # Overall emotional state
            emotional_stability = (emotion_scores.get("confidence", 0) + 
                                 (1 - emotion_scores.get("nervousness", 0)) + 
                                 (1 - emotion_scores.get("stress", 0))) / 3
            
            return {
                "primary_emotion": primary_emotion,
                "confidence_level": round(primary_score, 2),
                "emotion_scores": {k: round(v, 2) for k, v in emotion_scores.items()},
                "emotional_stability": round(emotional_stability, 2),
                "audio_indicators": {
                    "volume_variation": round(volume_variation, 2),
                    "speech_patterns": "analyzed" if len(words) > 5 else "insufficient_data"
                },
                "recommendations": self._generate_emotion_recommendations(emotion_scores),
                "overall_emotional_tone": self._determine_emotional_tone(emotion_scores)
            }
            
        except Exception as e:
            print(f"⚠️ Emotion detection error: {e}")
            return {
                "error": f"Emotion detection failed: {e}",
                "primary_emotion": "neutral",
                "emotional_stability": 5.0
            }

    def _generate_speech_feedback(self, overall_score: float, speech_rate: float, filler_count: int) -> str:
        """Generate speech feedback based on analysis."""
        feedback_parts = []
        
        if overall_score >= 8:
            feedback_parts.append("Excellent speech quality!")
        elif overall_score >= 6:
            feedback_parts.append("Good speech quality overall.")
        else:
            feedback_parts.append("Speech quality could be improved.")
        
        if speech_rate > 180:
            feedback_parts.append("Consider speaking a bit slower for clarity.")
        elif speech_rate < 120:
            feedback_parts.append("You can speak a bit faster to maintain engagement.")
        
        if filler_count > 3:
            feedback_parts.append("Try to reduce filler words for clearer communication.")
        
        return " ".join(feedback_parts)

    def _generate_speech_recommendations(self, clarity: float, pace: float, fluency: float) -> List[str]:
        """Generate speech improvement recommendations."""
        recommendations = []
        
        if clarity < 6:
            recommendations.append("Speak more clearly and articulate words")
        if pace < 6:
            recommendations.append("Adjust speaking pace for better comprehension")
        if fluency < 6:
            recommendations.append("Reduce filler words and practice smooth delivery")
        
        if not recommendations:
            recommendations.append("Maintain your current excellent speaking style")
        
        return recommendations

    def _generate_emotion_recommendations(self, emotion_scores: Dict[str, float]) -> List[str]:
        """Generate emotion-based recommendations."""
        recommendations = []
        
        if emotion_scores.get("nervousness", 0) > 0.3:
            recommendations.append("Take deep breaths to reduce nervousness")
        if emotion_scores.get("confidence", 0) < 0.3:
            recommendations.append("Show more confidence in your responses")
        if emotion_scores.get("enthusiasm", 0) < 0.2:
            recommendations.append("Express more enthusiasm about your experiences")
        
        if not recommendations:
            recommendations.append("Great emotional balance in your responses")
        
        return recommendations

    def _determine_emotional_tone(self, emotion_scores: Dict[str, float]) -> str:
        """Determine overall emotional tone."""
        positive_score = emotion_scores.get("confidence", 0) + emotion_scores.get("enthusiasm", 0) + emotion_scores.get("positivity", 0)
        negative_score = emotion_scores.get("nervousness", 0) + emotion_scores.get("stress", 0)
        
        if positive_score > negative_score * 1.5:
            return "positive"
        elif negative_score > positive_score * 1.5:
            return "negative"
        else:
            return "neutral"

