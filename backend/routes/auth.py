"""
Auth Routes
Google OAuth 2.0 flow + JWT session management.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import httpx

from backend.database import get_db
from backend.models.models import User, UserProfile
from backend.schemas.schemas import TokenResponse, GoogleAuthRequest
from backend.utils.jwt_handler import create_access_token
from backend.config import get_settings

router = APIRouter(prefix="/auth", tags=["Authentication"])
settings = get_settings()

GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"
GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"


@router.get("/google/login")
async def google_login():
    """Redirect user to Google OAuth consent screen."""
    params = {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "redirect_uri": settings.GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "offline",
        "prompt": "consent",
    }
    query = "&".join(f"{k}={v}" for k, v in params.items())
    return RedirectResponse(url=f"{GOOGLE_AUTH_URL}?{query}")


@router.get("/google/callback")
async def google_callback(code: str, db: AsyncSession = Depends(get_db)):
    """
    Handle Google OAuth callback.
    Exchange code → access token → user info → JWT.
    """
    # 1. Exchange code for tokens
    async with httpx.AsyncClient() as client:
        token_resp = await client.post(
            GOOGLE_TOKEN_URL,
            data={
                "code": code,
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "redirect_uri": settings.GOOGLE_REDIRECT_URI,
                "grant_type": "authorization_code",
            },
        )
        if token_resp.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to exchange Google token.")

        tokens = token_resp.json()
        access_token = tokens.get("access_token")

        # 2. Fetch user info from Google
        user_resp = await client.get(
            GOOGLE_USERINFO_URL,
            headers={"Authorization": f"Bearer {access_token}"},
        )
        if user_resp.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to fetch Google user info.")

        google_user = user_resp.json()

    google_id = google_user.get("id")
    email = google_user.get("email")
    name = google_user.get("name", email)
    avatar_url = google_user.get("picture")

    # 3. Upsert user in DB
    result = await db.execute(select(User).where(User.google_id == google_id))
    user = result.scalar_one_or_none()

    if not user:
        # Check if email already exists (registered differently)
        result2 = await db.execute(select(User).where(User.email == email))
        user = result2.scalar_one_or_none()

    if not user:
        user = User(google_id=google_id, email=email, name=name, avatar_url=avatar_url)
        db.add(user)
        await db.flush()

        profile = UserProfile(user_id=user.id)
        db.add(profile)
        await db.flush()
    else:
        user.google_id = google_id
        user.name = name
        user.avatar_url = avatar_url

    await db.commit()
    await db.refresh(user)

    # 4. Check survey status
    prof_result = await db.execute(select(UserProfile).where(UserProfile.user_id == user.id))
    profile = prof_result.scalar_one_or_none()
    survey_done = profile.survey_completed if profile else False

    # 5. Issue JWT
    jwt_token = create_access_token({"sub": user.id})

    # 6. Redirect frontend with token
    redirect_url = (
        f"{settings.FRONTEND_URL}/frontend/pages/f2gH7q.html"
        f"?token={jwt_token}"
        f"&survey={str(survey_done).lower()}"
        f"&name={name}"
    )
    return RedirectResponse(url=redirect_url)


@router.post("/exchange", response_model=TokenResponse)
async def exchange_code(body: GoogleAuthRequest, db: AsyncSession = Depends(get_db)):
    """
    Alternative: exchange Google auth code via JSON body (SPA flow).
    Returns JWT + user info directly.
    """
    async with httpx.AsyncClient() as client:
        token_resp = await client.post(
            GOOGLE_TOKEN_URL,
            data={
                "code": body.code,
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "redirect_uri": settings.GOOGLE_REDIRECT_URI,
                "grant_type": "authorization_code",
            },
        )
        if token_resp.status_code != 200:
            raise HTTPException(status_code=400, detail="Invalid authorization code.")
        tokens = token_resp.json()

        user_resp = await client.get(
            GOOGLE_USERINFO_URL,
            headers={"Authorization": f"Bearer {tokens['access_token']}"},
        )
        google_user = user_resp.json()

    result = await db.execute(select(User).where(User.google_id == google_user["id"]))
    user = result.scalar_one_or_none()

    if not user:
        user = User(
            google_id=google_user["id"],
            email=google_user["email"],
            name=google_user.get("name", google_user["email"]),
            avatar_url=google_user.get("picture"),
        )
        db.add(user)
        await db.flush()
        profile = UserProfile(user_id=user.id)
        db.add(profile)

    await db.commit()
    await db.refresh(user)

    prof_result = await db.execute(select(UserProfile).where(UserProfile.user_id == user.id))
    profile = prof_result.scalar_one_or_none()

    jwt_token = create_access_token({"sub": user.id})
    return TokenResponse(
        access_token=jwt_token,
        user_id=user.id,
        name=user.name,
        email=user.email,
        avatar_url=user.avatar_url,
        survey_completed=profile.survey_completed if profile else False,
    )
