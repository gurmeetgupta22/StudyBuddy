"""
Export Routes
PDF export for notes and test papers.
"""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.database import get_db
from backend.models.models import User, Note, Test
from backend.services.pdf_service import generate_notes_pdf, generate_test_pdf
from backend.utils.dependencies import get_current_user

router = APIRouter(prefix="/export", tags=["Export"])


@router.get("/notes/{note_id}/pdf")
async def export_note_pdf(
    note_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Export a note as a professionally formatted PDF."""
    result = await db.execute(
        select(Note).where(Note.id == note_id, Note.user_id == current_user.id)
    )
    note = result.scalar_one_or_none()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found.")

    # Reconstruct structured data from stored markdown + questions
    note_data = {
        "title": note.title,
        "overview": "",
        "sections": _parse_markdown_sections(note.content),
        "key_formulas": [],
        "common_mistakes": [],
        "summary": "",
        "questions": note.questions or [],
    }

    pdf_bytes = generate_notes_pdf(note_data, user_name=current_user.name)
    safe_title = "".join(c for c in note.title if c.isalnum() or c in " -_")[:50]

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{safe_title}.pdf"',
            "Content-Length": str(len(pdf_bytes)),
        },
    )


@router.get("/test/{test_id}/pdf")
async def export_test_pdf(
    test_id: str,
    answers: bool = False,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Export a test as a PDF exam paper. Set ?answers=true to include answer key."""
    result = await db.execute(
        select(Test).where(Test.id == test_id, Test.user_id == current_user.id)
    )
    test = result.scalar_one_or_none()
    if not test:
        raise HTTPException(status_code=404, detail="Test not found.")

    test_data = {
        "title": f"{test.subject} — Test Paper",
        "subject": test.subject,
        "difficulty": test.difficulty.value,
        "total_marks": sum(
            q.get("marks", 1)
            for sec in test.sections
            for q in sec.get("questions", [])
        ),
        "sections": test.sections,
    }

    pdf_bytes = generate_test_pdf(test_data, user_name=current_user.name, include_answers=answers)
    suffix = "_with_answers" if answers else ""
    safe_subject = "".join(c for c in test.subject if c.isalnum() or c in " -_")[:30]

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{safe_subject}_test{suffix}.pdf"',
            "Content-Length": str(len(pdf_bytes)),
        },
    )


def _parse_markdown_sections(content: str) -> list:
    """Parse markdown content into sections list for PDF generation."""
    sections = []
    current_section = None
    lines = content.split("\n")

    for line in lines:
        if line.startswith("## "):
            if current_section:
                sections.append(current_section)
            current_section = {
                "heading": line[3:].strip(),
                "content": "",
                "examples": [],
                "formula": None,
            }
        elif line.startswith("# "):
            continue  # Skip top-level title
        elif current_section:
            if line.startswith("> **Formula:**"):
                current_section["formula"] = line.replace("> **Formula:**", "").strip()
            elif line.startswith("- ") and "Example" in current_section.get("content", ""):
                current_section["examples"].append(line[2:].strip())
            else:
                current_section["content"] += line + "\n"

    if current_section:
        sections.append(current_section)

    return sections
