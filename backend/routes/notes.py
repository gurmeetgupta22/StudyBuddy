"""
Notes Routes
AI-powered study notes generation, retrieval, bookmarking.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import List

from backend.database import get_db
from backend.models.models import User, UserProfile, Note
from backend.schemas.schemas import NoteGenerateRequest, NoteResponse, NoteListItem, MessageResponse
from backend.services.ai_service import generate_notes
from backend.utils.dependencies import get_current_user

router = APIRouter(prefix="/notes", tags=["Notes"])


async def _get_profile_dict(user_id: str, db: AsyncSession):
    """Helper: fetch user profile as plain dict for AI personalization."""
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


def _build_markdown(parsed: dict) -> str:
    """Convert parsed AI response dict into full markdown string."""
    md = f"# {parsed.get('title', '')}\n\n"
    md += f"{parsed.get('overview', '')}\n\n"

    for sec in parsed.get("sections", []):
        md += f"## {sec.get('heading', '')}\n\n"
        md += f"{sec.get('content', '')}\n\n"
        if sec.get("examples"):
            md += "**Examples:**\n"
            for ex in sec["examples"]:
                md += f"- {ex}\n"
            md += "\n"
        if sec.get("formula"):
            md += f"> **Formula:** {sec['formula']}\n\n"

    if parsed.get("key_formulas"):
        md += "## Key Formulas\n\n"
        for f in parsed["key_formulas"]:
            md += f"- {f}\n"
        md += "\n"

    if parsed.get("common_mistakes"):
        md += "## Common Mistakes\n\n"
        for m in parsed["common_mistakes"]:
            md += f"- ! {m}\n"
        md += "\n"

    if parsed.get("summary"):
        md += f"## Summary\n\n{parsed['summary']}\n"

    return md


@router.post("/generate", response_model=NoteResponse)
async def generate_note(
    body: NoteGenerateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Generate AI study notes for a topic and store in DB."""
    profile_dict = await _get_profile_dict(current_user.id, db)

    try:
        parsed = await generate_notes(body.topic, profile_dict)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"AI generation failed: {str(e)}",
        )

    markdown_content = _build_markdown(parsed)

    note = Note(
        user_id=current_user.id,
        topic=body.topic,
        title=parsed.get("title", body.topic),
        content=markdown_content,
        questions=parsed.get("questions", []),
        tags=parsed.get("tags", []),
    )
    db.add(note)
    await db.commit()
    await db.refresh(note)

    return NoteResponse(
        id=note.id,
        topic=note.topic,
        title=note.title,
        content=note.content,
        questions=note.questions,
        is_bookmarked=note.is_bookmarked,
        tags=note.tags,
        created_at=note.created_at,
    )


@router.get("/", response_model=List[NoteListItem])
async def list_notes(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all notes for the current user (newest first)."""
    result = await db.execute(
        select(Note)
        .where(Note.user_id == current_user.id)
        .order_by(desc(Note.created_at))
    )
    notes = result.scalars().all()
    return [
        NoteListItem(
            id=n.id,
            topic=n.topic,
            title=n.title,
            is_bookmarked=n.is_bookmarked,
            created_at=n.created_at,
        )
        for n in notes
    ]


@router.get("/{note_id}", response_model=NoteResponse)
async def get_note(
    note_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a single note by ID."""
    result = await db.execute(
        select(Note).where(Note.id == note_id, Note.user_id == current_user.id)
    )
    note = result.scalar_one_or_none()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found.")
    return NoteResponse(
        id=note.id,
        topic=note.topic,
        title=note.title,
        content=note.content,
        questions=note.questions,
        is_bookmarked=note.is_bookmarked,
        tags=note.tags,
        created_at=note.created_at,
    )


@router.post("/{note_id}/bookmark", response_model=MessageResponse)
async def toggle_bookmark(
    note_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Toggle bookmark status for a note."""
    result = await db.execute(
        select(Note).where(Note.id == note_id, Note.user_id == current_user.id)
    )
    note = result.scalar_one_or_none()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found.")

    note.is_bookmarked = not note.is_bookmarked
    await db.commit()
    action = "bookmarked" if note.is_bookmarked else "removed from bookmarks"
    return MessageResponse(message=f"Note {action}.")


@router.delete("/{note_id}", response_model=MessageResponse)
async def delete_note(
    note_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a note."""
    result = await db.execute(
        select(Note).where(Note.id == note_id, Note.user_id == current_user.id)
    )
    note = result.scalar_one_or_none()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found.")
    await db.delete(note)
    await db.commit()
    return MessageResponse(message="Note deleted.")
