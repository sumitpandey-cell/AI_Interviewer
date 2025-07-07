"""
Google Cloud Storage service for file uploads
"""

import os
import uuid
from typing import Optional, BinaryIO
from datetime import datetime, timedelta

try:
    from google.cloud import storage
    from google.oauth2 import service_account
    GOOGLE_CLOUD_AVAILABLE = True
except ImportError:
    GOOGLE_CLOUD_AVAILABLE = False

from ai_interviewer.config import settings


class CloudStorageService:
    """Service for managing file uploads to Google Cloud Storage."""
    
    def __init__(self):
        self.bucket_name = os.getenv("GCS_BUCKET_NAME", "ai-interviewer-files")
        self.client = None
        
        if GOOGLE_CLOUD_AVAILABLE:
            try:
                # Initialize Google Cloud Storage client
                if os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
                    self.client = storage.Client()
                else:
                    # For development, create a mock client
                    self.client = None
            except Exception as e:
                print(f"Warning: Could not initialize Google Cloud Storage: {e}")
                self.client = None
    
    async def upload_file(
        self, 
        file_data: BinaryIO, 
        filename: str,
        content_type: str = "application/octet-stream",
        folder: str = "uploads"
    ) -> str:
        """
        Upload a file to Google Cloud Storage.
        
        Args:
            file_data: Binary file data
            filename: Original filename
            content_type: MIME type of the file
            folder: Folder within the bucket to store the file
            
        Returns:
            str: Public URL of the uploaded file
        """
        if not self.client:
            # For development/testing, return a mock URL
            mock_url = f"https://storage.googleapis.com/{self.bucket_name}/{folder}/{uuid.uuid4()}_{filename}"
            return mock_url
        
        try:
            # Generate unique filename
            file_extension = os.path.splitext(filename)[1]
            unique_filename = f"{uuid.uuid4()}{file_extension}"
            blob_name = f"{folder}/{datetime.now().strftime('%Y/%m/%d')}/{unique_filename}"
            
            # Get bucket
            bucket = self.client.bucket(self.bucket_name)
            blob = bucket.blob(blob_name)
            
            # Upload file
            blob.upload_from_file(file_data, content_type=content_type)
            
            # Make the blob publicly readable (optional)
            blob.make_public()
            
            return blob.public_url
            
        except Exception as e:
            raise Exception(f"Failed to upload file: {str(e)}")
    
    async def upload_audio_file(self, file_data: BinaryIO, filename: str) -> str:
        """Upload an audio file specifically."""
        return await self.upload_file(
            file_data=file_data,
            filename=filename,
            content_type="audio/wav",
            folder="audio"
        )
    
    async def upload_video_file(self, file_data: BinaryIO, filename: str) -> str:
        """Upload a video file specifically."""
        return await self.upload_file(
            file_data=file_data,
            filename=filename,
            content_type="video/mp4",
            folder="video"
        )
    
    def generate_signed_url(self, blob_name: str, expiration_hours: int = 1) -> str:
        """
        Generate a signed URL for private file access.
        
        Args:
            blob_name: Name of the blob in storage
            expiration_hours: Hours until the URL expires
            
        Returns:
            str: Signed URL
        """
        if not self.client:
            return f"https://mock-storage-url.com/{blob_name}"
        
        try:
            bucket = self.client.bucket(self.bucket_name)
            blob = bucket.blob(blob_name)
            
            expiration = datetime.utcnow() + timedelta(hours=expiration_hours)
            
            url = blob.generate_signed_url(
                version="v4",
                expiration=expiration,
                method="GET"
            )
            
            return url
            
        except Exception as e:
            raise Exception(f"Failed to generate signed URL: {str(e)}")


# Global storage service instance
storage_service = CloudStorageService()
