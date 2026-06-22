"""
Analytics Routes
Learning performance dashboard data.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List
from collections import Counter

from backend.database import get_db
from backend.models.models import User, Note, Test
from backend.schemas.schemas import AnalyticsResponse
from backend.utils.dependencies import get_current_user

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/", response_model=AnalyticsResponse)
async def get_analytics(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Return comprehensive analytics for the user's learning journey."""
    # Notes stats
    notes_result = await db.execute(
        select(Note).where(Note.user_id == current_user.id)
    )
    notes = notes_result.scalars().all()
    total_notes = len(notes)
    bookmarked = sum(1 for n in notes if n.is_bookmarked)
    recent_topics = [n.topic for n in sorted(notes, key=lambda x: x.created_at, reverse=True)[:5]]

    # Test stats
    tests_result = await db.execute(
        select(Test).where(Test.user_id == current_user.id)
    )
    tests = tests_result.scalars().all()
    total_tests = len(tests)
    completed_tests = sum(1 for t in tests if t.completed)

    accuracies = [t.accuracy for t in tests if t.accuracy is not None]
    avg_accuracy = round(sum(accuracies) / len(accuracies), 1) if accuracies else None

    # Weak areas (aggregate wrong_topics across all tests)
    all_wrong = []
    for t in tests:
        if t.wrong_topics:
            all_wrong.extend(t.wrong_topics)
    weak_areas = [topic for topic, _ in Counter(all_wrong).most_common(5)]

    # Accuracy trend (last 10 completed tests)
    completed = [t for t in tests if t.completed and t.accuracy is not None]
    completed.sort(key=lambda x: x.created_at)
    accuracy_trend = [
        {
            "date": t.created_at.strftime("%b %d"),
            "accuracy": t.accuracy,
            "subject": t.subject,
        }
        for t in completed[-10:]
    ]

    return AnalyticsResponse(
        total_notes=total_notes,
        total_tests=total_tests,
        completed_tests=completed_tests,
        average_accuracy=avg_accuracy,
        bookmarked_notes=bookmarked,
        weak_areas=weak_areas,
        recent_topics=recent_topics,
        accuracy_trend=accuracy_trend,
    )
