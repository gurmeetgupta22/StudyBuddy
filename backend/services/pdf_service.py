"""
PDF Export Service
Generates professional-looking PDFs for notes and tests using ReportLab.
"""
import io
import re
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, HRFlowable,
    Table, TableStyle, PageBreak,
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


# ---------------------------------------------------------------------------
# Color Palette
# ---------------------------------------------------------------------------
PRIMARY = colors.HexColor("#6C63FF")
SECONDARY = colors.HexColor("#2D2B55")
ACCENT = colors.HexColor("#FF6584")
LIGHT_BG = colors.HexColor("#F4F3FF")
TEXT_DARK = colors.HexColor("#1A1A2E")
TEXT_MID = colors.HexColor("#4A4A6A")
BORDER = colors.HexColor("#E0DEFF")


def _base_styles():
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "SBTitle",
        parent=styles["Title"],
        fontSize=24,
        textColor=PRIMARY,
        spaceAfter=6,
        fontName="Helvetica-Bold",
        alignment=TA_CENTER,
    )
    heading1 = ParagraphStyle(
        "SBH1",
        parent=styles["Heading1"],
        fontSize=16,
        textColor=SECONDARY,
        spaceBefore=14,
        spaceAfter=6,
        fontName="Helvetica-Bold",
        borderPad=4,
    )
    heading2 = ParagraphStyle(
        "SBH2",
        parent=styles["Heading2"],
        fontSize=13,
        textColor=PRIMARY,
        spaceBefore=10,
        spaceAfter=4,
        fontName="Helvetica-Bold",
    )
    body = ParagraphStyle(
        "SBBody",
        parent=styles["Normal"],
        fontSize=10,
        textColor=TEXT_DARK,
        leading=16,
        spaceAfter=6,
        alignment=TA_JUSTIFY,
        fontName="Helvetica",
    )
    meta = ParagraphStyle(
        "SBMeta",
        parent=styles["Normal"],
        fontSize=9,
        textColor=TEXT_MID,
        alignment=TA_CENTER,
        spaceAfter=4,
    )
    question = ParagraphStyle(
        "SBQ",
        parent=styles["Normal"],
        fontSize=10,
        textColor=SECONDARY,
        leading=14,
        spaceBefore=8,
        spaceAfter=4,
        fontName="Helvetica-Bold",
    )
    answer = ParagraphStyle(
        "SBAns",
        parent=styles["Normal"],
        fontSize=10,
        textColor=TEXT_DARK,
        leading=14,
        leftIndent=12,
        spaceAfter=6,
    )

    return {
        "title": title_style,
        "h1": heading1,
        "h2": heading2,
        "body": body,
        "meta": meta,
        "question": question,
        "answer": answer,
    }


def _clean_md(text: str) -> str:
    """Convert basic markdown to ReportLab-compatible markup."""
    if not text:
        return ""
    
    # Escape special characters
    text = text.replace("&", "&amp;")
    text = text.replace("<", "&lt;")
    text = text.replace(">", "&gt;")
    
    # Bold
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    # Italic
    text = re.sub(r"_(.+?)_", r"<i>\1</i>", text)
    
    # Inline code
    text = re.sub(r"`([^`]+)`", r'<font name="Courier" color="#6C63FF">\1</font>', text)
    
    # Code blocks
    def code_repl(m):
        code_content = m.group(1)
        # Preserve indentation by converting spaces to non-breaking spaces
        code_content = code_content.replace(" ", "&nbsp;")
        code_content = code_content.replace("\n", "<br/>")
        # Use a distinct color for the block
        return f'<br/><font name="Courier" color="#6C63FF">{code_content}</font><br/>'
        
    text = re.sub(r"```(?:[\w]*)\n([\s\S]+?)```", code_repl, text)
    
    # Replace remaining newlines with <br/> to preserve paragraph breaks
    text = text.replace("\n", "<br/>")
    
    return text


def generate_notes_pdf(note_data: dict, user_name: str = "Student") -> bytes:
    """
    Generate a professional PDF from note data dict.
    note_data expected keys: title, overview, sections, key_formulas,
                             common_mistakes, summary, questions
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm,
        title=note_data.get("title", "Study Notes"),
        author="StudyBuddy",
    )

    styles = _base_styles()
    story = []

    # ---- Header ----
    story.append(Paragraph("StudyBuddy", styles["meta"]))
    story.append(Paragraph(note_data.get("title", "Study Notes"), styles["title"]))
    story.append(Paragraph(
        f"Generated for: {user_name}  |  {datetime.now().strftime('%B %d, %Y')}",
        styles["meta"],
    ))
    story.append(HRFlowable(width="100%", thickness=2, color=PRIMARY, spaceAfter=12))

    # ---- Overview ----
    if note_data.get("overview"):
        story.append(Paragraph("Overview", styles["h1"]))
        story.append(Paragraph(_clean_md(note_data["overview"]), styles["body"]))
        story.append(Spacer(1, 8))

    # ---- Sections ----
    for sec in note_data.get("sections", []):
        story.append(Paragraph(sec.get("heading", ""), styles["h1"]))
        story.append(Paragraph(_clean_md(sec.get("content", "")), styles["body"]))

        if sec.get("examples"):
            story.append(Paragraph("<b>Examples:</b>", styles["body"]))
            for ex in sec["examples"]:
                story.append(Paragraph(f"• {_clean_md(ex)}", styles["body"]))

        if sec.get("formula"):
            formula_para = Paragraph(
                f"<b>Formula:</b> {sec['formula']}",
                ParagraphStyle(
                    "formula",
                    parent=styles["body"],
                    backColor=LIGHT_BG,
                    borderColor=PRIMARY,
                    borderWidth=1,
                    borderPad=6,
                    borderRadius=4,
                ),
            )
            story.append(formula_para)
        story.append(Spacer(1, 6))

    # ---- Key Formulas ----
    if note_data.get("key_formulas"):
        story.append(HRFlowable(width="100%", thickness=1, color=BORDER))
        story.append(Paragraph("Key Formulas", styles["h1"]))
        for f in note_data["key_formulas"]:
            story.append(Paragraph(f"• {f}", styles["body"]))

    # ---- Common Mistakes ----
    if note_data.get("common_mistakes"):
        story.append(Paragraph("Common Mistakes to Avoid", styles["h1"]))
        for m in note_data["common_mistakes"]:
            story.append(Paragraph(f"! {_clean_md(m)}", styles["body"]))

    # ---- Summary ----
    if note_data.get("summary"):
        story.append(HRFlowable(width="100%", thickness=1, color=BORDER, spaceBefore=8))
        story.append(Paragraph("Summary", styles["h1"]))
        story.append(Paragraph(_clean_md(note_data["summary"]), styles["body"]))

    # ---- Questions ----
    questions = note_data.get("questions", [])
    if questions:
        story.append(PageBreak())
        story.append(Paragraph("Practice Questions", styles["h1"]))
        story.append(HRFlowable(width="100%", thickness=2, color=PRIMARY, spaceAfter=8))

        for i, q in enumerate(questions, 1):
            qtype = q.get("type", "").upper()
            story.append(Paragraph(
                f"Q{i}. [{qtype}] {_clean_md(q.get('question', ''))}",
                styles["question"],
            ))
            if q.get("options"):
                for opt in q["options"]:
                    story.append(Paragraph(f"  {opt}", styles["body"]))
            story.append(Paragraph(
                f"<b>Answer:</b> {_clean_md(q.get('answer', ''))}",
                styles["answer"],
            ))
            if q.get("explanation"):
                story.append(Paragraph(
                    f"<i>Explanation: {_clean_md(q['explanation'])}</i>",
                    styles["answer"],
                ))
            story.append(Spacer(1, 6))

    doc.build(story)
    return buffer.getvalue()


def generate_test_pdf(test_data: dict, user_name: str = "Student", include_answers: bool = False) -> bytes:
    """
    Generate a professional exam-paper-style PDF from test data.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm,
        title=test_data.get("title", "Test Paper"),
        author="StudyBuddy",
    )

    styles = _base_styles()
    story = []

    # ---- Exam Header ----
    story.append(Paragraph("StudyBuddy — Test Paper", styles["meta"]))
    story.append(HRFlowable(width="100%", thickness=3, color=PRIMARY, spaceAfter=6))
    story.append(Paragraph(test_data.get("title", "Test"), styles["title"]))

    info_data = [
        ["Subject", test_data.get("subject", "—"), "Difficulty", test_data.get("difficulty", "—").capitalize()],
        ["Total Marks", str(test_data.get("total_marks", "—")), "Date", datetime.now().strftime("%d/%m/%Y")],
        ["Student", user_name, "Time", "As per syllabus"],
    ]
    info_table = Table(info_data, colWidths=[3.5*cm, 6*cm, 3.5*cm, 4*cm])
    info_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), LIGHT_BG),
        ("BACKGROUND", (2, 0), (2, -1), LIGHT_BG),
        ("TEXTCOLOR", (0, 0), (-1, -1), TEXT_DARK),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME", (2, 0), (2, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("BOX", (0, 0), (-1, -1), 1, BORDER),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, BORDER),
        ("PADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 16))

    # ---- Sections ----
    for section in test_data.get("sections", []):
        sec_title = section.get("title", f"Section {section.get('section_number', '')}")
        story.append(Paragraph(sec_title, styles["h1"]))
        story.append(HRFlowable(width="100%", thickness=1, color=PRIMARY, spaceAfter=6))

        for q in section.get("questions", []):
            marks = q.get("marks", 1)
            story.append(Paragraph(
                f"<b>Q{q.get('number', '')}.</b> {_clean_md(q.get('question', ''))} "
                f"<font color='#6C63FF'>[{marks} mark{'s' if marks > 1 else ''}]</font>",
                styles["question"],
            ))

            if q.get("options"):
                for opt in q["options"]:
                    story.append(Paragraph(f"    {opt}", styles["body"]))

            if include_answers:
                story.append(Paragraph(
                    f"<b>Answer:</b> {_clean_md(q.get('answer', ''))}",
                    styles["answer"],
                ))
                if q.get("explanation"):
                    story.append(Paragraph(
                        f"<i>{_clean_md(q['explanation'])}</i>",
                        styles["answer"],
                    ))
            else:
                if section.get("question_type") != "mcq":
                    # Add blank lines for writing space
                    for _ in range(3):
                        story.append(HRFlowable(width="100%", thickness=0.5, color=colors.lightgrey, spaceAfter=12))

            story.append(Spacer(1, 4))

        story.append(Spacer(1, 12))

    # ---- Footer ----
    story.append(HRFlowable(width="100%", thickness=1, color=BORDER))
    story.append(Paragraph("Generated by StudyBuddy AI — studybuddy.app", styles["meta"]))

    doc.build(story)
    return buffer.getvalue()
