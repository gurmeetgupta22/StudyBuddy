"""
User Routes
Profile management and onboarding survey.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.database import get_db
from backend.models.models import User, UserProfile
from backend.schemas.schemas import SurveyRequest, UserProfileResponse, MessageResponse
from backend.utils.dependencies import get_current_user

router = APIRouter(prefix="/user", tags=["User"])


@router.get("/me", response_model=UserProfileResponse)
async def get_me(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Return current user's full profile."""
    result = await db.execute(
        select(UserProfile).where(UserProfile.user_id == current_user.id)
    )
    profile = result.scalar_one_or_none()

    return UserProfileResponse(
        id=current_user.id,
        email=current_user.email,
        name=current_user.name,
        avatar_url=current_user.avatar_url,
        age=profile.age if profile else None,
        occupation=profile.occupation.value if profile and profile.occupation else None,
        grade=profile.grade if profile else None,
        stream=profile.stream if profile else None,
        subjects=profile.subjects if profile else None,
        survey_completed=profile.survey_completed if profile else False,
    )


@router.post("/survey", response_model=MessageResponse)
async def submit_survey(
    body: SurveyRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Save onboarding survey data for AI personalization."""
    result = await db.execute(
        select(UserProfile).where(UserProfile.user_id == current_user.id)
    )
    profile = result.scalar_one_or_none()

    if not profile:
        profile = UserProfile(user_id=current_user.id)
        db.add(profile)

    profile.age = body.age
    profile.occupation = body.occupation
    profile.grade = body.grade
    profile.stream = body.stream
    profile.subjects = body.subjects
    profile.custom_occupation = body.custom_occupation
    profile.survey_completed = True

    await db.commit()
    return MessageResponse(message="Survey saved successfully.")


@router.put("/profile", response_model=MessageResponse)
async def update_profile(
    body: SurveyRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update user profile/preferences (re-run survey)."""
    result = await db.execute(
        select(UserProfile).where(UserProfile.user_id == current_user.id)
    )
    profile = result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found.")

    profile.age = body.age
    profile.occupation = body.occupation
    profile.grade = body.grade
    profile.stream = body.stream
    profile.subjects = body.subjects
    profile.custom_occupation = body.custom_occupation

    await db.commit()
    return MessageResponse(message="Profile updated successfully.")
