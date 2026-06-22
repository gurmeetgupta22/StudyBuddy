"""
StudyBuddy ORM Models
Defines all database tables using SQLAlchemy declarative base.
"""
from datetime import datetime
from sqlalchemy import (
    Column, String, Integer, Float, Boolean, DateTime,
    Text, ForeignKey, JSON, Enum as SAEnum
)
from sqlalchemy.orm import relationship
from backend.database import Base
import uuid
import enum


def _uuid() -> str:
    return str(uuid.uuid4())


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class OccupationType(str, enum.Enum):
    school = "school"
    college = "college"
    other = "other"


class DifficultyLevel(str, enum.Enum):
    easy = "easy"
    medium = "medium"
    hard = "hard"


class QuestionType(str, enum.Enum):
    mcq = "mcq"
    short = "short"
    medium = "medium"
    long = "long"
    programming = "programming"


# ---------------------------------------------------------------------------
# User & Profile
# ---------------------------------------------------------------------------

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=_uuid)
    google_id = Column(String, unique=True, index=True, nullable=True)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    avatar_url = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    profile = relationship("UserProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    notes = relationship("Note", back_populates="user", cascade="all, delete-orphan")
    tests = relationship("Test", back_populates="user", cascade="all, delete-orphan")


class UserProfile(Base):
    __tablename__ = "user_profiles"

    id = Column(String, primary_key=True, default=_uuid)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)

    # Survey fields
    age = Column(Integer, nullable=True)
    occupation = Column(SAEnum(OccupationType), nullable=True)

    # School-specific
    grade = Column(Integer, nullable=True)   # 6–12

    # College-specific
    stream = Column(String, nullable=True)   # e.g., "Computer Science"
    subjects = Column(JSON, nullable=True)   # List[str]

    # Other
    custom_occupation = Column(String, nullable=True)

    # Meta
    survey_completed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="profile")


# ---------------------------------------------------------------------------
# Notes
# ---------------------------------------------------------------------------

class Note(Base):
    __tablename__ = "notes"

    id = Column(String, primary_key=True, default=_uuid)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    topic = Column(String, nullable=False)
    title = Column(String, nullable=True)
    content = Column(Text, nullable=False)          # Full markdown content
    questions = Column(JSON, nullable=True)         # List of Q&A objects
    is_bookmarked = Column(Boolean, default=False)
    tags = Column(JSON, nullable=True)              # List[str]
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="notes")
    tests = relationship("Test", back_populates="note", cascade="all, delete-orphan")


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class Test(Base):
    __tablename__ = "tests"

    id = Column(String, primary_key=True, default=_uuid)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    note_id = Column(String, ForeignKey("notes.id", ondelete="SET NULL"), nullable=True)

    subject = Column(String, nullable=False)
    difficulty = Column(SAEnum(DifficultyLevel), default=DifficultyLevel.medium)
    sections = Column(JSON, nullable=False)         # Full structured test JSON
    total_questions = Column(Integer, default=0)
    mcq_score = Column(Integer, nullable=True)
    mcq_total = Column(Integer, nullable=True)
    accuracy = Column(Float, nullable=True)
    completed = Column(Boolean, default=False)
    wrong_topics = Column(JSON, nullable=True)      # List[str] weak areas

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="tests")
    note = relationship("Note", back_populates="tests")
