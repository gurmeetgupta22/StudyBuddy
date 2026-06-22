"""
Test Routes
AI-powered test generation, scoring, and retrieval.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import List

from backend.database import get_db
from backend.models.models import User, UserProfile, Note, Test
from backend.schemas.schemas import (
    TestGenerateRequest, TestScoreRequest,
    TestResponse, TestListItem, MessageResponse,
)
from backend.services.ai_service import generate_test
from backend.utils.dependencies import get_current_user

router = APIRouter(prefix="/test", tags=["Tests"])


async def _get_profile_dict(user_id: str, db: AsyncSession):
    result = await db.execute(select(UserProfile).where(UserProfile.user_id == user_id))
    profile = result.scalar_one_or_none()
    if not profile or not profile.survey_completed:
        return None
    return {
        "occupation": profile.occupation.value if profile.occupation else None,
        "grade": profile.grade,
        "stream": profile.stream,
        "subjects": profile.subjects,
    }


@router.post("/generate", response_model=TestResponse)
async def generate_test_route(
    body: TestGenerateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Generate an AI-powered test from a note/topic."""
    # Validate note ownership
    note_result = await db.execute(
        select(Note).where(Note.id == body.note_id, Note.user_id == current_user.id)
    )
    note = note_result.scalar_one_or_none()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found.")

    profile_dict = await _get_profile_dict(current_user.id, db)
    sections_config = [s.model_dump() for s in body.sections]

    try:
        test_data = await generate_test(
            topic=note.topic,
            subject=body.subject,
            difficulty=body.difficulty.value,
            sections_config=sections_config,
            profile=profile_dict,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"AI test generation failed: {str(e)}",
        )

    total_questions = sum(
        len(sec.get("questions", [])) for sec in test_data.get("sections", [])
    )

    test = Test(
        user_id=current_user.id,
        note_id=note.id,
        subject=body.subject,
        difficulty=body.difficulty,
        sections=test_data.get("sections", []),
        total_questions=total_questions,
    )
    db.add(test)
    await db.commit()
    await db.refresh(test)

    return TestResponse(
        id=test.id,
        subject=test.subject,
        difficulty=test.difficulty.value,
        sections=test.sections,
        total_questions=test.total_questions,
        mcq_score=test.mcq_score,
        mcq_total=test.mcq_total,
        accuracy=test.accuracy,
        completed=test.completed,
        created_at=test.created_at,
    )


@router.post("/score", response_model=MessageResponse)
async def submit_score(
    body: TestScoreRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Submit MCQ score for a completed test."""
    result = await db.execute(
        select(Test).where(Test.id == body.test_id, Test.user_id == current_user.id)
    )
    test = result.scalar_one_or_none()
    if not test:
        raise HTTPException(status_code=404, detail="Test not found.")

    test.mcq_score = body.mcq_score
    test.mcq_total = body.mcq_total
    test.accuracy = round((body.mcq_score / body.mcq_total) * 100, 1) if body.mcq_total else 0
    test.wrong_topics = body.wrong_topics or []
    test.completed = True

    await db.commit()
    return MessageResponse(message=f"Score saved. Accuracy: {test.accuracy}%")


@router.get("/", response_model=List[TestListItem])
async def list_tests(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all tests for the current user."""
    result = await db.execute(
        select(Test)
        .where(Test.user_id == current_user.id)
        .order_by(desc(Test.created_at))
    )
    tests = result.scalars().all()
    return [
        TestListItem(
            id=t.id,
            subject=t.subject,
            difficulty=t.difficulty.value,
            total_questions=t.total_questions,
            accuracy=t.accuracy,
            completed=t.completed,
            created_at=t.created_at,
        )
        for t in tests
    ]


@router.get("/{test_id}", response_model=TestResponse)
async def get_test(
    test_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a single test by ID."""
    result = await db.execute(
        select(Test).where(Test.id == test_id, Test.user_id == current_user.id)
    )
    test = result.scalar_one_or_none()
    if not test:
        raise HTTPException(status_code=404, detail="Test not found.")
    return TestResponse(
        id=test.id,
        subject=test.subject,
        difficulty=test.difficulty.value,
        sections=test.sections,
        total_questions=test.total_questions,
        mcq_score=test.mcq_score,
        mcq_total=test.mcq_total,
        accuracy=test.accuracy,
        completed=test.completed,
        created_at=test.created_at,
    )


@router.delete("/{test_id}", response_model=MessageResponse)
async def delete_test(
    test_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a test."""
    result = await db.execute(
        select(Test).where(Test.id == test_id, Test.user_id == current_user.id)
    )
    test = result.scalar_one_or_none()
    if not test:
        raise HTTPException(status_code=404, detail="Test not found.")
    await db.delete(test)
    await db.commit()
    return MessageResponse(message="Test deleted.")
