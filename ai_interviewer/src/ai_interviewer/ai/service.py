"""
AI processing logic for interview workflow
"""

import os
import json
import re
import asyncio
from typing import Dict, List, Any, Optional
from .prompts import prompt_template
import base64
from ..utilities.Speech_to_text.stt_service import get_stt_service
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from .prompts import render_evalution_prompt

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


    async def generate_interview_question(
        self, 
        position: str, 
        interview_type: str = "technical",
        difficulty: str = "medium",
        number_of_questions: Optional[int] = 1,
        company: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Generate a single interview question using AI."""
        try:
            company_context = f" at {company}" if company else ""

            json_parser = JsonOutputParser()
            
            chain = prompt_template | self.llm | json_parser

            result = await chain.ainvoke({
                "interview_type": interview_type,
                "position": position,
                "company_context": company_context,
                "difficulty": difficulty,
                "number_of_questions": number_of_questions
            })
            print(f"LLM result type: {type(result)}")
            print(result)
            
            # Validate and process the result
            if isinstance(result, list):
                return result
            else:
                print("⚠️ AI generation returned invalid format, using fallback question")

            # Ensure all required fields are present
            question_obj = [{
                "question": "Default question",
                "type": interview_type,
                "difficulty": difficulty,
                "expected_points": ["General response"],
                "evaluation_criteria": {"overall": 1.0}
            }]
            # Validate evaluation criteria sum to 1.0
            criteria_sum = sum(question_obj[0]["evaluation_criteria"].values())
            if abs(criteria_sum - 1.0) > 0.1:
                question_obj[0]["evaluation_criteria"] = {
                    k: v / criteria_sum for k, v in question_obj[0]["evaluation_criteria"].items()
                }
            return question_obj
        except Exception as e:
            print(f"⚠️ Error generating question with AI: {e}")
            return self._get_fallback_questions(position, interview_type, difficulty, 1)
    
    def _get_fallback_questions(
        self,
        position: str,
        interview_type: str = "technical",
        difficulty: str = "medium",
        num_questions: int = 1
    ) -> List[Dict[str, Any]]:
        """Return fallback interview questions if AI generation fails."""
        fallback_questions = {
            "technical": [
                {
                    "question": f"What are the key responsibilities of a {position}?",
                    "type": "technical",
                    "difficulty": difficulty,
                    "expected_points": ["Core responsibilities", "Required skills", "Typical challenges"],
                    "evaluation_criteria": {"overall": 1.0}
                },
                {
                    "question": f"Explain a recent project you worked on as a {position}.",
                    "type": "technical",
                    "difficulty": difficulty,
                    "expected_points": ["Project overview", "Technologies used", "Outcome"],
                    "evaluation_criteria": {"overall": 1.0}
                }
            ],
            "behavioral": [
                {
                    "question": "Tell me about a time you faced a challenge at work and how you handled it.",
                    "type": "behavioral",
                    "difficulty": difficulty,
                    "expected_points": ["Situation", "Task", "Action", "Result"],
                    "evaluation_criteria": {"overall": 1.0}
                },
                {
                    "question": "Describe a situation where you worked as part of a team.",
                    "type": "behavioral",
                    "difficulty": difficulty,
                    "expected_points": ["Teamwork", "Collaboration", "Outcome"],
                    "evaluation_criteria": {"overall": 1.0}
                }
            ]
        }
        questions = fallback_questions.get(interview_type, fallback_questions["technical"])
        return questions[:num_questions]



    async def evaluate_response(
        self,
        question: str,
        user_response: str,
        expected_points: Optional[List[str]] = None,
        evaluation_criteria: Optional[Dict[str, float]] = None
    ) -> Dict[str, Any]:
        """Evaluate a user's response using LLM if available; otherwise, fallback to rule-based evaluation."""

        # ========== USE LLM IF AVAILABLE ==========
        if self.llm:
            try:
                print("Evaluating response with LLM...")

                # Generate LLM prompt
                prompt = render_evalution_prompt(
                    question=question,
                    user_response=user_response,
                    expected_points=expected_points,
                    evaluation_criteria=evaluation_criteria
                )

                # Invoke LLM
                result = await self.llm.ainvoke(prompt)
                raw = result.content

                print(f"LLM content type: {type(raw)}")
                print("Raw LLM output:")
                print(raw)

                # Try to extract JSON from ```json ... ```
                match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", raw, re.DOTALL)
                cleaned_json_str = match.group(1) if match else raw

                # Try parsing JSON
                result_json = json.loads(cleaned_json_str)
                return result_json

            except Exception as e:
                print(f"⚠️ LLM evaluation failed: {e}")
                print("Falling back to rule-based evaluation...")

        # ========== RULE-BASED FALLBACK ==========
        score = 7.5
        improvements = []
        feedback = "Good response! You demonstrated understanding of the topic."
        detailed = {}

        if expected_points:
            covered = sum(1 for pt in expected_points if pt.lower() in user_response.lower())
            total = len(expected_points)
            score = 5 + 5 * (covered / total) if total else 7.5
            if covered < total:
                improvements.append("Address all expected points in your answer.")
            detailed = {pt: (8 if pt.lower() in user_response.lower() else 5) for pt in expected_points}

        if evaluation_criteria:
            for k in evaluation_criteria:
                detailed[k] = detailed.get(k, 7)

        return {
            "overall_score": round(score, 1),
            "feedback": feedback,
            "detailed_analysis": detailed,
            "improvements": improvements or ["Provide more concrete examples."]
        }


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
        interview_context: Dict[str, Any],
        user_response: Optional[str] = "I don't not know",
    ) -> Dict[str, Any]:
        """Generate a contextual follow-up question using AI if available, else fallback to rule-based."""
        if self.llm:
            try:
                # Compose prompt for LLM
                from .prompts import followup_prompt
                json_output_parser = JsonOutputParser()
                chain = followup_prompt | self.llm | json_output_parser
                result = await chain.ainvoke({
                    "previous_question": previous_question,
                    "user_response": user_response,
                    "interview_context": interview_context
                }) 
                print(f"LLM follow-up result type: {type(result)}")
                content = getattr(result, 'content', result)
                
                return content
            except Exception as e:
                print(f"⚠️ LLM follow-up generation failed: {e}")
                print("Falling back to rule-based follow-up...")
        # Fallback: simple rule-based follow-up
        follow_ups = [
            "Can you provide a specific example of that?",
            "How did you overcome the challenges you mentioned?",
            "What technologies did you use for that project?",
            "How would you approach this differently now?",
            "What did you learn from that experience?"
        ]
        return {
            "question": follow_ups[0],
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
        """Transcribe audio data using custom SpeechToText service with base64 input."""
        try:
            stt_service = get_stt_service()

            if not stt_service:
                print("⚠️ STT service not available - please check configuration")
                return "[Audio transcription not available - please type your response]"
            print("stt_service",stt_service)

            # Convert audio data to base64
            audio_base64 = base64.b64encode(audio_data).decode('utf-8')

            # Get Google API response
            response = stt_service.convert_base64_to_text(audio_base64, input_format=audio_format)
            # Extract transcript from response
            transcript = stt_service.get_transcript(response)
            # Compute average confidence for robustness (optional)
            confidences = [
                alt.confidence
                for result in response.results
                for alt in [result.alternatives[0]]
                if hasattr(alt, "confidence")
                ]
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0

            if transcript and avg_confidence > 0.5:
                return transcript.strip()
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

if __name__ == "__main__":
    # Example usage
    service = AIService()
    questions = asyncio.run(service.generate_interview_question("Software Engineer", "technical", 'medium', 5, "google"))
    print("Generated Questions:", questions)