"""
SQLAlchemy models for interviews
"""

from sqlalchemy import Column, Integer, String, Text, Float, DateTime, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped, mapped_column, relationship, DeclarativeBase
from typing import Optional, Dict, Any, List, TYPE_CHECKING

from ..database.base import Base
from ..auth.models import User  # adjust import to where your `User` model is defined

from typing import Optional, Literal
from sqlalchemy import String, Integer, Float, Text, ForeignKey, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..database.base import Base  # adjust import to where your `Base` is defined

from datetime import datetime  # ✅ Python's datetime class
from sqlalchemy import DateTime  # ✅ SQLAlchemy column type
if TYPE_CHECKING:
    from .models import Interview
    from .models import Question

InterviewStatus = Literal["created", "in_progress", "completed", "cancelled","paused"]
InterviewType = Literal["technical", "behavioral", "mixed"]

class Interview(Base):
    """Interview model."""

    __tablename__ = "interviews"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    position: Mapped[str] = mapped_column(String, nullable=False)
    company: Mapped[Optional[str]] = mapped_column(String)
    interview_type: Mapped[InterviewType] = mapped_column(String, nullable=False)  # Enforced via Literal
    status: Mapped[InterviewStatus] = mapped_column(String, default="created")
    duration_minutes: Mapped[float] = mapped_column(Float, default=60)
    score: Mapped[Optional[float]] = mapped_column(Float)
    feedback: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), server_default=func.now())
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="interviews")
    questions: Mapped[list["InterviewQuestion"]] = relationship(
        "InterviewQuestion", back_populates="interview", cascade="all, delete-orphan"
    )
    answers: Mapped[list["Answer"]] = relationship(
        "Answer", back_populates="interview", cascade="all, delete-orphan"
    )

class Question(Base):
    """Question model."""
    
    __tablename__ = "questions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    question_type: Mapped[str] = mapped_column(String, nullable=False)  # multiple_choice, open_ended, coding
    category: Mapped[str] = mapped_column(String, nullable=False)
    difficulty: Mapped[str] = mapped_column(String, default="medium")  # easy, medium, hard
    options: Mapped[Optional[dict]] = mapped_column(JSON)  # For multiple choice questions
    correct_answer: Mapped[Optional[str]] = mapped_column(Text)
    explanation: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    interview_questions: Mapped[List["InterviewQuestion"]] = relationship(
        "InterviewQuestion", back_populates="question"
    )


class InterviewQuestion(Base):
    """Interview-Question association model."""
    
    __tablename__ = "interview_questions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    interview_id: Mapped[int] = mapped_column(ForeignKey("interviews.id"), nullable=False)
    question_id: Mapped[int] = mapped_column(ForeignKey("questions.id"), nullable=False)
    order: Mapped[int] = mapped_column(nullable=False)
    is_answered: Mapped[bool] = mapped_column(default=False)

    # Relationships
    interview: Mapped["Interview"] = relationship("Interview", back_populates="questions")
    question: Mapped["Question"] = relationship("Question", back_populates="interview_questions")



class Answer(Base):
    """Answer model."""
    
    __tablename__ = "answers"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    interview_id: Mapped[int] = mapped_column(ForeignKey("interviews.id"), nullable=False)
    question_id: Mapped[int] = mapped_column(ForeignKey("questions.id"), nullable=False)
    answer_text: Mapped[str] = mapped_column(Text, nullable=False)
    is_correct: Mapped[Optional[bool]] = mapped_column()
    score: Mapped[Optional[float]] = mapped_column()
    feedback: Mapped[Optional[str]] = mapped_column(Text)
    time_taken: Mapped[Optional[int]] = mapped_column()  # in seconds
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    interview: Mapped["Interview"] = relationship("Interview", back_populates="answers")
    question: Mapped["Question"] = relationship("Question")


class InterviewSession(Base):
    """Real-time interview session model for LangGraph workflow."""

    __tablename__ = "interview_sessions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    interview_id: Mapped[int] = mapped_column(ForeignKey("interviews.id"), nullable=False)
    session_token: Mapped[str] = mapped_column(unique=True, nullable=False)

    # LangGraph workflow state
    current_question_id: Mapped[Optional[int]] = mapped_column(ForeignKey("interview_questions.id"))
    workflow_state: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)  # ✅ Pylance will now accept dict
    step_history: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSON)

    # Session status
    is_active: Mapped[bool] = mapped_column(default=True)
    session_status: Mapped[str] = mapped_column(default="initialized")

    # Current session context
    current_step: Mapped[Optional[str]] = mapped_column()
    ai_context: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)

    # Timestamps
    created_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())
    last_activity_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    interview: Mapped["Interview"] = relationship("Interview")
    current_question: Mapped[Optional["InterviewQuestion"]] = relationship("InterviewQuestion", foreign_keys=[current_question_id])
# Removed AudioVideoFile model and all related code for real-time streaming only

# Add relationship to User model (this would typically be in auth/models.py)
# User.interviews = relationship("Interview", back_populates="user")
