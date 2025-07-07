"""
WebSocket module for real-time communication
"""

from .manager import websocket_manager
from .router import router as websocket_router

__all__ = ["websocket_manager", "websocket_router"]
