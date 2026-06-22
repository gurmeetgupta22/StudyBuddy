"""
AI Service
Handles all communication with OpenRouter LLM API.
Includes carefully engineered prompts for notes and test generation.
"""
import json
import re
import httpx
from typing import Optional
from backend.config import get_settings

settings = get_settings()

HEADERS = {
    "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
    "Content-Type": "application/json",
    "HTTP-Referer": "https://studybuddy.app",
    "X-Title": "StudyBuddy",
}


def _personalization_context(profile: Optional[dict]) -> str:
    """Build personalization context string from user profile."""
    if not profile:
        return "Explain at a general undergraduate level with clear language."

    occ = profile.get("occupation")
    if occ == "school":
        grade = profile.get("grade", 8)
        if grade <= 7:
            return f"The student is in Grade {grade}. Use very simple language, short sentences, relatable everyday examples. Avoid jargon."
        elif grade <= 9:
            return f"The student is in Grade {grade}. Use simple but slightly technical language, analogies, and step-by-step breakdowns."
        else:
            return f"The student is in Grade {grade} (high school). Use moderately technical language. Include formulas where relevant."
    elif occ == "college":
        stream = profile.get("stream", "general")
        subjects = profile.get("subjects", [])
        subj_str = ", ".join(subjects) if subjects else "general subjects"
        return f"The student studies {stream} ({subj_str}) at college level. Use technical, in-depth explanations with precise terminology."
    else:
        return "Use clear, professional language suited to an adult learner."


async def generate_notes(topic: str, profile: Optional[dict] = None) -> dict:
    """
    Call OpenRouter to generate structured study notes.
    Returns a dict with 'title', 'content' (markdown), 'questions', 'tags'.
    """
    personalization = _personalization_context(profile)

    system_prompt = """You are StudyBuddy AI, an expert educational content creator. 
Your job is to generate comprehensive, structured study notes in strict JSON format.
Always respond with valid JSON only — no markdown fences, no extra text."""

    user_prompt = f"""Generate detailed study notes for the topic: "{topic}"

Personalization instruction: {personalization}

Return ONLY a valid JSON object with this exact structure:
{{
  "title": "Clear, engaging title for the topic",
  "tags": ["tag1", "tag2", "tag3"],
  "overview": "2-3 sentence overview of the topic",
  "sections": [
    {{
      "heading": "Section Heading",
      "content": "Detailed content with markdown formatting (use **bold**, _italic_, bullet lists). ALWAYS use ```language ... ``` blocks for any code.",
      "examples": [
        "Example description:\n```c\n// ACTUAL CODE GOES HERE\nint x = 10;\n```",
        "Another example:\n```python\nprint('code block')\n```"
      ],
      "formula": "Optional formula if applicable, else null"
    }}
  ],
  "visual_explanation": "ASCII or text-based diagram if helpful, else null",
  "key_formulas": ["formula1", "formula2"],
  "common_mistakes": ["Mistake 1", "Mistake 2"],
  "summary": "Concise 3-5 sentence summary",
  "questions": [
    {{
      "type": "mcq",
      "question": "Question text?",
      "options": ["A) Option1", "B) Option2", "C) Option3", "D) Option4"],
      "answer": "A) Option1",
      "explanation": "Why this is correct"
    }},
    {{
      "type": "short",
      "question": "Short answer question?",
      "answer": "Concise answer in 2-3 sentences",
      "explanation": null
    }},
    {{
      "type": "long",
      "question": "Long answer question?",
      "answer": "Detailed answer with multiple points",
      "explanation": null
    }}
  ]
}}

Rules:
- Generate 3 MCQs, 2 short-answer, 1 long-answer questions
- sections array must have at least 4 sections covering core concepts
- All JSON must be valid — escape any special characters properly
- Adapt depth and language to the personalization instruction"""

    payload = {
        "model": settings.OPENROUTER_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.7,
        "max_tokens": 4000,
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            f"{settings.OPENROUTER_BASE_URL}/chat/completions",
            headers=HEADERS,
            json=payload,
        )
        response.raise_for_status()
        data = response.json()

    raw_content = data["choices"][0]["message"]["content"].strip()

    # Strip markdown code fences if model wraps response
    raw_content = re.sub(r"^```(?:json)?\s*", "", raw_content)
    raw_content = re.sub(r"\s*```$", "", raw_content)

    parsed = json.loads(raw_content)
    return parsed


async def generate_test(
    topic: str,
    subject: str,
    difficulty: str,
    sections_config: list,
    profile: Optional[dict] = None,
) -> dict:
    """
    Call OpenRouter to generate a structured test.
    sections_config: list of {"question_type": str, "count": int}
    Returns a dict with 'sections' array.
    """
    personalization = _personalization_context(profile)

    sections_desc = "\n".join(
        [f"- Section {i+1}: {s['question_type'].upper()} × {s['count']} questions"
         for i, s in enumerate(sections_config)]
    )

    difficulty_map = {
        "easy": "straightforward questions testing basic recall and understanding",
        "medium": "moderately challenging questions requiring application of concepts",
        "hard": "difficult questions requiring deep analysis, synthesis, and critical thinking",
    }

    system_prompt = """You are StudyBuddy AI, an expert exam paper creator.
Generate structured test papers in strict JSON format only.
Never wrap the response in markdown. Output raw JSON only."""

    user_prompt = f"""Create a test paper on the topic: "{topic}"
Subject: {subject}
Difficulty: {difficulty} — {difficulty_map.get(difficulty, '')}
Personalization: {personalization}

Required sections:
{sections_desc}

Return ONLY a valid JSON object:
{{
  "title": "Test title",
  "subject": "{subject}",
  "difficulty": "{difficulty}",
  "total_marks": <integer>,
  "sections": [
    {{
      "section_number": 1,
      "title": "Section Title (e.g., Multiple Choice Questions)",
      "question_type": "mcq",
      "questions": [
        {{
          "number": 1,
          "question": "Question text?",
          "options": ["A) ...", "B) ...", "C) ...", "D) ..."],
          "answer": "A) ...",
          "marks": 1,
          "explanation": "Brief explanation"
        }}
      ]
    }},
    {{
      "section_number": 3,
      "title": "Programming Questions",
      "question_type": "programming",
      "questions": [
        {{
          "number": 1,
          "question": "Problem Statement\\n\\nYou are required to implement...\\n\\nInput Format...\\nConstraints...\\nOutput Format...\\nSample Input...\\nSample Output...",
          "answer": "```c\\n#include <stdio.h>\\nint main() {{ ... }}\\n```",
          "marks": 10,
          "explanation": "Explanation of the logic",
          "language": "c",
          "starter_code": "#include <stdio.h>\\n\\nint main() {{\\n    // Read inputs from stdin\\n    // Write output to stdout\\n    return 0;\\n}}",
          "test_cases": [
            {{"input": "5\\n1 2 3", "expected": "10 15 1 3"}},
            {{"input": "3\\n10", "expected": "20"}}
          ]
        }}
      ]
    }}
  ]
}}

Rules:
- STRICTLY use the exact `question_type` requested in 'Required sections'. If a section is 'programming', the type MUST be 'programming'.
- You MUST generate EXACTLY the number of questions requested for EACH section in the 'Required sections' block. Do not skip any questions.
- For mcq: always include 4 options A-D, correct answer, explanation
- For short: answer in 2-4 sentences
- For medium: answer in 1-2 paragraphs  
- For long: detailed answer with multiple sections
- For programming: The `question` MUST be structured like a LeetCode problem (Problem Statement, Input Format, Constraints, Output Format, Sample Input/Output). It must be directly related to the topic. The `answer` MUST be a full, working code block in markdown (` ```c ... ``` `). You MUST include `"language"` (e.g. 'c', 'python' - strictly lowercase) and an array of EXACTLY 5 `"test_cases"` with `"input"` and `"expected"` output.
- Marks: mcq=1, short=3, medium=5, long=10, programming=10"""

    payload = {
        "model": settings.OPENROUTER_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.6,
        "max_tokens": 4000,
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            f"{settings.OPENROUTER_BASE_URL}/chat/completions",
            headers=HEADERS,
            json=payload,
        )
        response.raise_for_status()
        data = response.json()

    raw_content = data["choices"][0]["message"]["content"].strip()
    raw_content = re.sub(r"^```(?:json)?\s*", "", raw_content)
    raw_content = re.sub(r"\s*```$", "", raw_content)

    parsed = json.loads(raw_content)
    return parsed
