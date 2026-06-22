"""
Pydantic Schemas
All request/response models for the API.
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Any
from datetime import datetime
from enum import Enum


# ---------------------------------------------------------------------------
# Enums (mirror ORM enums)
# ---------------------------------------------------------------------------

class OccupationType(str, Enum):
    school = "school"
    college = "college"
    other = "other"


class DifficultyLevel(str, Enum):
    easy = "easy"
    medium = "medium"
    hard = "hard"


class QuestionType(str, Enum):
    mcq = "mcq"
    short = "short"
    medium = "medium"
    long = "long"
    programming = "programming"


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------

class GoogleAuthRequest(BaseModel):
    code: str = Field(..., description="OAuth authorization code from Google")


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    name: str
    email: str
    avatar_url: Optional[str] = None
    survey_completed: bool = False


# ---------------------------------------------------------------------------
# User / Profile
# ---------------------------------------------------------------------------

class SurveyRequest(BaseModel):
    age: int = Field(..., ge=5, le=100)
    occupation: OccupationType
    grade: Optional[int] = Field(None, ge=6, le=12)
    stream: Optional[str] = None
    subjects: Optional[List[str]] = None
    custom_occupation: Optional[str] = None


class UserProfileResponse(BaseModel):
    id: str
    email: str
    name: str
    avatar_url: Optional[str]
    age: Optional[int]
    occupation: Optional[str]
    grade: Optional[int]
    stream: Optional[str]
    subjects: Optional[List[str]]
    survey_completed: bool

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------------
# Notes
# ---------------------------------------------------------------------------

class NoteGenerateRequest(BaseModel):
    topic: str = Field(..., min_length=3, max_length=300)


class QuestionItem(BaseModel):
    type: str                          # mcq | short | long
    question: str
    options: Optional[List[str]] = None  # For MCQ
    answer: str
    explanation: Optional[str] = None


class NoteResponse(BaseModel):
    id: str
    topic: str
    title: str
    content: str
    questions: Optional[List[dict]] = None
    is_bookmarked: bool
    tags: Optional[List[str]]
    created_at: datetime

    class Config:
        from_attributes = True


class NoteListItem(BaseModel):
    id: str
    topic: str
    title: str
    is_bookmarked: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestSectionConfig(BaseModel):
    question_type: QuestionType
    count: int = Field(..., ge=1, le=20)


class TestGenerateRequest(BaseModel):
    note_id: str
    subject: str
    difficulty: DifficultyLevel = DifficultyLevel.medium
    sections: List[TestSectionConfig] = Field(..., min_length=1)


class TestScoreRequest(BaseModel):
    test_id: str
    mcq_score: int
    mcq_total: int
    wrong_topics: Optional[List[str]] = None


class TestResponse(BaseModel):
    id: str
    subject: str
    difficulty: str
    sections: List[dict]
    total_questions: int
    mcq_score: Optional[int]
    mcq_total: Optional[int]
    accuracy: Optional[float]
    completed: bool
    created_at: datetime

    class Config:
        from_attributes = True


class TestListItem(BaseModel):
    id: str
    subject: str
    difficulty: str
    total_questions: int
    accuracy: Optional[float]
    completed: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------------
# Analytics
# ---------------------------------------------------------------------------

class AnalyticsResponse(BaseModel):
    total_notes: int
    total_tests: int
    completed_tests: int
    average_accuracy: Optional[float]
    bookmarked_notes: int
    weak_areas: List[str]
    recent_topics: List[str]
    accuracy_trend: List[dict]   # [{date, accuracy}]


# ---------------------------------------------------------------------------
# Generic
# ---------------------------------------------------------------------------

class MessageResponse(BaseModel):
    message: str
    success: bool = True
