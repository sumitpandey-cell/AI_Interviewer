"""
WebSocket connection manager for real-time interview communication
"""

import json
import logging
from typing import Dict, List, Optional
from fastapi import WebSocket, WebSocketDisconnect
from datetime import datetime

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages WebSocket connections for interview sessions."""
    
    def __init__(self):
        # Active connections: {session_token: WebSocket}
        self.active_connections: Dict[str, WebSocket] = {}
        # Connection metadata: {session_token: {user_id, connected_at, etc}}
        self.connection_metadata: Dict[str, Dict] = {}
        # Audio buffers for streaming: {session_token: [audio_chunks]}
        self.audio_buffers: Dict[str, List[bytes]] = {}
        # Streaming speech recognition clients: {session_token: {client, active}}
        self.streaming_clients: Dict[str, Dict] = {}
    
    async def connect(self, websocket: WebSocket, session_token: str, user_id: int):
        """Accept a new WebSocket connection."""
        await websocket.accept()
        self.active_connections[session_token] = websocket
        self.connection_metadata[session_token] = {
            "user_id": user_id,
            "connected_at": datetime.now(),
            "status": "connected"
        }
        self.audio_buffers[session_token] = []
        
        logger.info(f"WebSocket connected for session {session_token}, user {user_id}")
        
        # Send connection confirmation
        await self.send_personal_message(session_token, {
            "type": "connection_established",
            "session_token": session_token,
            "message": "WebSocket connection established",
            "timestamp": datetime.now().isoformat()
        })
    
    def disconnect(self, session_token: str):
        """Remove a WebSocket connection."""
        if session_token in self.active_connections:
            del self.active_connections[session_token]
        if session_token in self.connection_metadata:
            del self.connection_metadata[session_token]
        if session_token in self.audio_buffers:
            del self.audio_buffers[session_token]
        if session_token in self.streaming_clients:
            # Close any streaming clients
            try:
                if self.streaming_clients[session_token].get('client'):
                    self.streaming_clients[session_token]['client'].finish()
            except Exception as e:
                logger.error(f"Error closing streaming client: {e}")
            del self.streaming_clients[session_token]
        
        logger.info(f"WebSocket disconnected for session {session_token}")
    
    async def send_personal_message(self, session_token: str, message: Dict):
        """Send a message to a specific session."""
        if session_token in self.active_connections:
            try:
                websocket = self.active_connections[session_token]
                await websocket.send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"Error sending message to {session_token}: {e}")
                # Remove dead connection
                self.disconnect(session_token)
    
    async def broadcast_to_session(self, session_token: str, message: Dict):
        """Broadcast message to a session (alias for send_personal_message)."""
        await self.send_personal_message(session_token, message)
    
    async def send_transcript_update(self, session_token: str, partial_transcript: str, confidence: float):
        """Send live transcript update."""
        message = {
            "type": "transcript_update",
            "partial_transcript": partial_transcript,
            "confidence": confidence,
            "timestamp": datetime.now().isoformat()
        }
        await self.send_personal_message(session_token, message)
    
    async def send_audio_processing_status(self, session_token: str, status: str, data: Optional[Dict] = None):
        """Send audio processing status updates."""
        message = {
            "type": "audio_processing",
            "status": status,
            "data": data or {},
            "timestamp": datetime.now().isoformat()
        }
        await self.send_personal_message(session_token, message)
    
    async def send_evaluation_update(self, session_token: str, evaluation_data: Dict):
        """Send real-time evaluation updates."""
        message = {
            "type": "evaluation_update",
            "evaluation": evaluation_data,
            "timestamp": datetime.now().isoformat()
        }
        await self.send_personal_message(session_token, message)
    
    async def send_question_update(self, session_token: str, question_data: Dict):
        """Send new question to frontend."""
        message = {
            "type": "question_update", 
            "question": question_data,
            "timestamp": datetime.now().isoformat()
        }
        await self.send_personal_message(session_token, message)
    
    async def send_interview_status(self, session_token: str, status: str, data: Optional[Dict] = None):
        """Send interview status updates."""
        message = {
            "type": "interview_status",
            "status": status,
            "data": data or {},
            "timestamp": datetime.now().isoformat()
        }
        await self.send_personal_message(session_token, message)
    
    async def send_error(self, session_token: str, error_type: str, error_message: str):
        """Send error messages."""
        message = {
            "type": "error",
            "error_type": error_type,
            "message": error_message,
            "timestamp": datetime.now().isoformat()
        }
        await self.send_personal_message(session_token, message)
    
    def add_audio_chunk(self, session_token: str, audio_chunk: bytes):
        """Add audio chunk to buffer."""
        if session_token not in self.audio_buffers:
            self.audio_buffers[session_token] = []
        self.audio_buffers[session_token].append(audio_chunk)
    
    def get_complete_audio(self, session_token: str) -> Optional[bytes]:
        """Get complete audio from chunks and clear buffer."""
        if session_token in self.audio_buffers:
            complete_audio = b''.join(self.audio_buffers[session_token])
            self.audio_buffers[session_token] = []  # Clear buffer
            return complete_audio
        return None
    
    def is_connected(self, session_token: str) -> bool:
        """Check if session is connected."""
        return session_token in self.active_connections
    
    def get_connection_info(self, session_token: str) -> Optional[Dict]:
        """Get connection metadata."""
        return self.connection_metadata.get(session_token)
    
    def get_active_sessions(self) -> List[str]:
        """Get list of active session tokens."""
        return list(self.active_connections.keys())


# Global WebSocket manager instance
websocket_manager = ConnectionManager()
