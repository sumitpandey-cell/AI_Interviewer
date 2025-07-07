"""
SQLAlchemy models for interviews
"""

from sqlalchemy import Column, Integer, String, Text, Float, DateTime, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..database.base import Base


class Interview(Base):
    """Interview model."""
    __tablename__ = "interviews"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text)
    position = Column(String, nullable=False)
    company = Column(String)
    interview_type = Column(String, nullable=False)  # technical, behavioral, mixed
    status = Column(String, default="created")  # created, in_progress, completed, cancelled
    duration_minutes = Column(Integer, default=60)
    score = Column(Float)
    feedback = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="interviews")
    questions = relationship("InterviewQuestion", back_populates="interview", cascade="all, delete-orphan")
    answers = relationship("Answer", back_populates="interview", cascade="all, delete-orphan")


class Question(Base):
    """Question model."""
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(Text, nullable=False)
    question_type = Column(String, nullable=False)  # multiple_choice, open_ended, coding
    category = Column(String, nullable=False)
    difficulty = Column(String, default="medium")  # easy, medium, hard
    options = Column(JSON)  # For multiple choice questions
    correct_answer = Column(Text)
    explanation = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    interview_questions = relationship("InterviewQuestion", back_populates="question")


class InterviewQuestion(Base):
    """Interview-Question association model."""
    __tablename__ = "interview_questions"

    id = Column(Integer, primary_key=True, index=True)
    interview_id = Column(Integer, ForeignKey("interviews.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    order = Column(Integer, nullable=False)
    is_answered = Column(Boolean, default=False)

    # Relationships
    interview = relationship("Interview", back_populates="questions")
    question = relationship("Question", back_populates="interview_questions")


class Answer(Base):
    """Answer model."""
    __tablename__ = "answers"

    id = Column(Integer, primary_key=True, index=True)
    interview_id = Column(Integer, ForeignKey("interviews.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    answer_text = Column(Text, nullable=False)
    is_correct = Column(Boolean)
    score = Column(Float)
    feedback = Column(Text)
    time_taken = Column(Integer)  # in seconds
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    interview = relationship("Interview", back_populates="answers")
    question = relationship("Question")


class InterviewSession(Base):
    """Real-time interview session model for LangGraph workflow."""
    
    __tablename__ = "interview_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    interview_id = Column(Integer, ForeignKey("interviews.id"), nullable=False)
    session_token = Column(String, unique=True, nullable=False)
    
    # LangGraph workflow state
    current_question_id = Column(Integer, ForeignKey("interview_questions.id"))
    workflow_state = Column(JSON)  # Current LangGraph state
    step_history = Column(JSON)  # History of workflow steps
    
    # Session status
    is_active = Column(Boolean, default=True)
    session_status = Column(String, default="initialized")  # initialized, started, question_presented, awaiting_response, evaluating, completed
    
    # Current session context
    current_step = Column(String)  # current step in LangGraph
    ai_context = Column(JSON)  # AI processing context
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_activity_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    interview = relationship("Interview")
    current_question = relationship("InterviewQuestion", foreign_keys=[current_question_id])


class AudioVideoFile(Base):
    """Model for storing audio/video files metadata."""
    
    __tablename__ = "audio_video_files"
    
    id = Column(Integer, primary_key=True, index=True)
    interview_id = Column(Integer, ForeignKey("interviews.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("interview_questions.id"))
    
    # File information
    file_type = Column(String, nullable=False)  # audio, video
    file_format = Column(String)  # mp3, wav, mp4, etc.
    file_size_bytes = Column(Integer)
    duration_seconds = Column(Float)
    
    # Google Cloud Storage information
    gcs_bucket = Column(String)
    gcs_object_path = Column(String)
    gcs_url = Column(String)
    
    # Processing status
    upload_status = Column(String, default="pending")  # pending, uploading, completed, failed
    transcription_status = Column(String, default="pending")  # pending, processing, completed, failed
    transcription_text = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    interview = relationship("Interview")
    question = relationship("InterviewQuestion")

# Add relationship to User model (this would typically be in auth/models.py)
# User.interviews = relationship("Interview", back_populates="user")
