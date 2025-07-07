"""
Cloud storage service for media files
"""

import logging
from typing import Optional, Dict, Any
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from ..config import settings

logger = logging.getLogger(__name__)


class StorageService:
    """Cloud storage service for audio/video files."""
    
    def __init__(self):
        self.aws_access_key = getattr(settings, 'AWS_ACCESS_KEY_ID', "")
        self.aws_secret_key = getattr(settings, 'AWS_SECRET_ACCESS_KEY', "")
        self.bucket_name = getattr(settings, 'AWS_S3_BUCKET', "ai-interviewer-media")
        self.region = getattr(settings, 'AWS_REGION', "us-east-1")
        
        self.s3_client = None
        self._initialize_s3()
    
    def _initialize_s3(self):
        """Initialize S3 client if credentials are available."""
        try:
            if self.aws_access_key and self.aws_secret_key:
                self.s3_client = boto3.client(
                    's3',
                    aws_access_key_id=self.aws_access_key,
                    aws_secret_access_key=self.aws_secret_key,
                    region_name=self.region
                )
                logger.info("S3 client initialized successfully")
            else:
                logger.warning("AWS credentials not found, S3 storage unavailable")
        except Exception as e:
            logger.error(f"Failed to initialize S3 client: {e}")
    
    async def upload_audio_file(self, audio_data: bytes, session_token: str, file_format: str = "webm") -> Optional[str]:
        """Upload audio file to cloud storage."""
        try:
            if not self.s3_client:
                logger.warning("S3 client not available, using local storage fallback")
                return await self._save_local_file(audio_data, session_token, "audio", file_format)
            
            # Generate unique file key
            file_key = f"audio/{session_token}/{session_token}_audio.{file_format}"
            
            # Upload to S3
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=file_key,
                Body=audio_data,
                ContentType=f"audio/{file_format}"
            )
            
            # Generate URL
            file_url = f"https://{self.bucket_name}.s3.{self.region}.amazonaws.com/{file_key}"
            logger.info(f"Audio file uploaded successfully: {file_url}")
            return file_url
            
        except ClientError as e:
            logger.error(f"S3 upload failed: {e}")
            return await self._save_local_file(audio_data, session_token, "audio", file_format)
        except Exception as e:
            logger.error(f"Audio upload failed: {e}")
            return None
    
    async def upload_video_file(self, video_data: bytes, session_token: str, file_format: str = "webm") -> Optional[str]:
        """Upload video file to cloud storage."""
        try:
            if not self.s3_client:
                return await self._save_local_file(video_data, session_token, "video", file_format)
            
            file_key = f"video/{session_token}/{session_token}_video.{file_format}"
            
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=file_key,
                Body=video_data,
                ContentType=f"video/{file_format}"
            )
            
            file_url = f"https://{self.bucket_name}.s3.{self.region}.amazonaws.com/{file_key}"
            logger.info(f"Video file uploaded successfully: {file_url}")
            return file_url
            
        except Exception as e:
            logger.error(f"Video upload failed: {e}")
            return None
    
    async def _save_local_file(self, data: bytes, session_token: str, file_type: str, file_format: str) -> str:
        """Fallback to local file storage."""
        try:
            import os
            from pathlib import Path
            
            # Create storage directory
            storage_dir = Path("media_storage") / file_type / session_token
            storage_dir.mkdir(parents=True, exist_ok=True)
            
            # Save file
            file_path = storage_dir / f"{session_token}_{file_type}.{file_format}"
            with open(file_path, "wb") as f:
                f.write(data)
            
            # Return relative URL
            relative_url = f"/media/{file_type}/{session_token}/{session_token}_{file_type}.{file_format}"
            logger.info(f"File saved locally: {relative_url}")
            return relative_url
            
        except Exception as e:
            logger.error(f"Local file save failed: {e}")
            return ""
    
    async def get_file_url(self, file_key: str) -> Optional[str]:
        """Get presigned URL for file access."""
        try:
            if not self.s3_client:
                return f"/media/{file_key}"  # Local file URL
            
            # Generate presigned URL (valid for 1 hour)
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': file_key},
                ExpiresIn=3600
            )
            return url
            
        except Exception as e:
            logger.error(f"Failed to generate file URL: {e}")
            return None
    
    async def delete_file(self, file_key: str) -> bool:
        """Delete file from storage."""
        try:
            if not self.s3_client:
                # Delete local file
                import os
                local_path = f"media_storage/{file_key}"
                if os.path.exists(local_path):
                    os.remove(local_path)
                return True
            
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=file_key)
            logger.info(f"File deleted: {file_key}")
            return True
            
        except Exception as e:
            logger.error(f"File deletion failed: {e}")
            return False
