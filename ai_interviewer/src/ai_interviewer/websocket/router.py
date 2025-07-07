"""
WebSocket router for real-time interview communication
"""

import json
import base64
import logging
from typing import Optional
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException
from sqlalchemy.orm import Session

from .manager import websocket_manager
from ..database.session import get_db
from ..interviews.models import InterviewSession
from ..auth.dependencies import get_current_user
from ..ai.service import AIService

router = APIRouter()
logger = logging.getLogger(__name__)

ai_service = AIService()


@router.websocket("/interview/{session_token}")
async def websocket_interview_endpoint(
    websocket: WebSocket,
    session_token: str,
    token: Optional[str] = None
):
    """WebSocket endpoint for real-time interview communication."""
    try:
        # Note: WebSocket authentication is tricky, in production you'd want
        # to implement proper token validation here
        await websocket_manager.connect(websocket, session_token, user_id=1)  # Simplified for demo
        
        try:
            while True:
                # Receive message from client
                data = await websocket.receive_text()
                message = json.loads(data)
                
                await handle_websocket_message(session_token, message)
                
        except WebSocketDisconnect:
            websocket_manager.disconnect(session_token)
            logger.info(f"WebSocket disconnected for session {session_token}")
            
    except Exception as e:
        logger.error(f"WebSocket error for session {session_token}: {e}")
        await websocket_manager.send_error(session_token, "connection_error", str(e))


async def handle_websocket_message(session_token: str, message: dict):
    """Handle incoming WebSocket messages."""
    message_type = message.get("type")
    
    try:
        if message_type == "audio_chunk":
            await handle_audio_chunk(session_token, message)
        
        elif message_type == "audio_final":
            await handle_final_audio(session_token, message)
        
        elif message_type == "ping":
            await websocket_manager.send_personal_message(session_token, {
                "type": "pong",
                "timestamp": message.get("timestamp")
            })
        
        elif message_type == "get_status":
            await handle_status_request(session_token)
        
        else:
            logger.warning(f"Unknown message type: {message_type}")
            await websocket_manager.send_error(session_token, "unknown_message", f"Unknown message type: {message_type}")
            
    except Exception as e:
        logger.error(f"Error handling message {message_type}: {e}")
        await websocket_manager.send_error(session_token, "processing_error", str(e))


async def handle_audio_chunk(session_token: str, message: dict):
    """Handle streaming audio chunks."""
    try:
        # Decode base64 audio chunk
        audio_data = message.get("audio_data", "")
        chunk_sequence = message.get("chunk_sequence", 0)
        
        if audio_data:
            audio_bytes = base64.b64decode(audio_data)
            websocket_manager.add_audio_chunk(session_token, audio_bytes)
            
            # Process chunk for real-time transcription (if supported)
            if ai_service.speech_client:
                try:
                    # Note: Google Speech API supports streaming, but this is a simplified version
                    partial_transcript = await process_audio_chunk_for_transcript(audio_bytes)
                    if partial_transcript:
                        await websocket_manager.send_transcript_update(
                            session_token, 
                            partial_transcript, 
                            confidence=0.8  # Mock confidence for demo
                        )
                except Exception as e:
                    logger.warning(f"Real-time transcription failed: {e}")
            
            # Send acknowledgment
            await websocket_manager.send_personal_message(session_token, {
                "type": "audio_chunk_ack",
                "chunk_sequence": chunk_sequence,
                "status": "received"
            })
            
    except Exception as e:
        logger.error(f"Error processing audio chunk: {e}")
        await websocket_manager.send_error(session_token, "audio_processing_error", str(e))


async def handle_final_audio(session_token: str, message: dict):
    """Handle final audio processing."""
    try:
        # Get complete audio from chunks
        complete_audio = websocket_manager.get_complete_audio(session_token)
        
        if complete_audio:
            # Send processing status
            await websocket_manager.send_audio_processing_status(
                session_token, 
                "processing",
                {"message": "Processing complete audio..."}
            )
            
            # Transcribe complete audio
            if ai_service.speech_client:
                try:
                    transcript = await transcribe_complete_audio(complete_audio)
                    
                    # Send final transcript
                    await websocket_manager.send_personal_message(session_token, {
                        "type": "final_transcript",
                        "transcript": transcript,
                        "confidence": 0.95
                    })
                    
                    # Analyze speech quality
                    speech_analysis = await analyze_speech_quality(complete_audio)
                    if speech_analysis:
                        await websocket_manager.send_personal_message(session_token, {
                            "type": "speech_analysis",
                            "analysis": speech_analysis
                        })
                    
                    await websocket_manager.send_audio_processing_status(
                        session_token,
                        "complete",
                        {"transcript": transcript}
                    )
                    
                except Exception as e:
                    logger.error(f"Audio processing failed: {e}")
                    await websocket_manager.send_error(session_token, "transcription_error", str(e))
            else:
                await websocket_manager.send_error(session_token, "service_unavailable", "Speech service not available")
        else:
            await websocket_manager.send_error(session_token, "no_audio", "No audio data received")
            
    except Exception as e:
        logger.error(f"Error processing final audio: {e}")
        await websocket_manager.send_error(session_token, "final_audio_error", str(e))


async def handle_status_request(session_token: str):
    """Handle status request."""
    connection_info = websocket_manager.get_connection_info(session_token)
    await websocket_manager.send_interview_status(session_token, "connected", {
        "connection_info": connection_info,
        "active_sessions": len(websocket_manager.get_active_sessions())
    })


async def process_audio_chunk_for_transcript(audio_chunk: bytes) -> Optional[str]:
    """Process audio chunk for real-time transcription."""
    # This is a simplified version - real implementation would use streaming APIs
    # For now, return None (no real-time transcription)
    return None


async def transcribe_complete_audio(audio_data: bytes) -> str:
    """Transcribe complete audio using AI service."""
    try:
        # Use AI service to transcribe
        if ai_service.speech_client:
            from google.cloud import speech_v1p1beta1 as speech
            
            # Configure recognition
            config = speech.RecognitionConfig(
                encoding=speech.RecognitionConfig.AudioEncoding.WEBM_OPUS,
                sample_rate_hertz=48000,  # Adjust based on your audio format
                language_code="en-US",
                enable_automatic_punctuation=True,
            )
            
            audio = speech.RecognitionAudio(content=audio_data)
            
            # Perform transcription
            response = ai_service.speech_client.recognize(config=config, audio=audio)
            
            # Extract transcript
            transcript = ""
            for result in response.results:
                transcript += result.alternatives[0].transcript + " "
            
            return transcript.strip()
        else:
            return "Speech service not available"
            
    except Exception as e:
        logger.error(f"Transcription error: {e}")
        return f"Transcription failed: {str(e)}"


async def analyze_speech_quality(audio_data: bytes) -> Optional[dict]:
    """Analyze speech quality metrics."""
    try:
        # Mock speech analysis for demo
        # In real implementation, you'd use audio analysis libraries or external APIs
        return {
            "clarity_score": 8.5,
            "pace_score": 7.8,
            "volume_level": "appropriate",
            "confidence_indicators": ["steady_pace", "clear_pronunciation"],
            "suggestions": ["Speak slightly slower for better clarity"]
        }
    except Exception as e:
        logger.error(f"Speech analysis error: {e}")
        return None


# Utility functions for other services to send WebSocket messages
async def notify_question_ready(session_token: str, question_data: dict):
    """Notify frontend that a new question is ready."""
    await websocket_manager.send_question_update(session_token, question_data)


async def notify_evaluation_complete(session_token: str, evaluation_data: dict):
    """Notify frontend that evaluation is complete."""
    await websocket_manager.send_evaluation_update(session_token, evaluation_data)


async def notify_interview_complete(session_token: str, final_data: dict):
    """Notify frontend that interview is complete."""
    await websocket_manager.send_interview_status(session_token, "completed", final_data)
