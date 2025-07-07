"""
External APIs integration module
"""

from .speech_service import SpeechService
from .storage_service import StorageService  
from .notification_service import NotificationService
from .video_analysis import VideoAnalysisService

__all__ = [
    "SpeechService",
    "StorageService", 
    "NotificationService",
    "VideoAnalysisService"
]
