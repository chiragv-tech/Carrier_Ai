"""Validate and extract text and structured signals from PDF resumes using PyMuPDF."""
from __future__ import annotations
import re
import fitz

SKILL_ALIASES = {
    "python": ["python"], "java": ["java"], "javascript": ["javascript", "js"],
    "html": ["html"], "css": ["css"], "sql": ["sql", "mysql", "postgresql", "sqlite"],
    "pandas": ["pandas"], "numpy": ["numpy"], "scikit-learn": ["scikit-learn", "sklearn"],
    "machine learning": ["machine learning", "ml"], "deep learning": ["deep learning"],
    "tensorflow": ["tensorflow"], "pytorch": ["pytorch"], "statistics": ["statistics", "statistical"],
    "data visualization": ["data visualization", "visualization", "plotly", "power bi", "tableau"],
    "excel": ["excel", "spreadsheets"], "git": ["git", "github", "gitlab"],
    "rest api": ["rest api", "restful api", "api integration"], "flask": ["flask"],
    "fastapi": ["fastapi"], "django": ["django"], "streamlit": ["streamlit"],
    "react": ["react", "react.js"], "data structures": ["data structures", "dsa"],
    "algorithms": ["algorithms", "algorithm design"], "oop": ["object-oriented", "oop"],
    "testing": ["unit testing", "pytest", "testing", "test cases"],
    "data cleaning": ["data cleaning", "data preprocessing", "data wrangling"],
    "feature engineering": ["feature engineering"], "model evaluation": ["model evaluation", "precision", "recall", "f1-score"],
    "c++": ["c++"], "c": [" c ", "c programming"], "linux": ["linux"],
    "cloud": ["aws", "azure", "google cloud", "cloud computing"], "docker": ["docker"],
}
SECTION_HEADERS = {
    "education": ["education", "academic background", "qualifications"],
    "projects": ["projects", "academic projects", "personal projects"],
    "experience": ["experience", "work experience", "internship", "employment"],
    "certifications": ["certifications", "certificates", "licenses"],
}

def extract_pdf_text(file_bytes: bytes) -> str:
    if not file_bytes:
        raise ValueError("The uploaded file is empty.")
    if not file_bytes.startswith(b"%PDF"):
        raise ValueError("This file does not appear to be a valid PDF. Please upload a PDF resume.")
    try:
        with fitz.open(stream=file_bytes, filetype="pdf") as doc:
            if doc.page_count == 0:
                raise ValueError("The PDF has no pages.")
            if doc.page_count > 30:
                raise ValueError("Please upload a resume PDF with 30 pages or fewer.")
            text = "\n".join(page.get_text("text") for page in doc)
    except ValueError:
        raise
    except Exception as exc:
        raise ValueError("The PDF could not be read. It may be corrupted or password-protected.") from exc
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    if len(text) < 40:
        raise ValueError("Very little text was found. If this is a scanned image PDF, run OCR first and upload a text-searchable PDF.")
    return text

def _section_content(text: str, aliases: list[str]) -> str:
    lines = text.splitlines()
    start = None
    for i, line in enumerate(lines):
        normalized = re.sub(r"[^a-z ]", "", line.lower()).strip()
        if any(normalized == h or normalized.startswith(h + " ") for h in aliases):
            start = i + 1
            break
    if start is None:
        return ""
    next_headers = {h for group in SECTION_HEADERS.values() for h in group}
    collected = []
    for line in lines[start:]:
        normalized = re.sub(r"[^a-z ]", "", line.lower()).strip()
        if normalized in next_headers:
            break
        if line.strip():
            collected.append(line.strip())
        if len(collected) >= 12:
            break
    return " ".join(collected)[:1200]

def analyze_resume_text(text: str) -> dict:
    low = " " + re.sub(r"\s+", " ", text.lower()) + " "
    found = []
    for skill, aliases in SKILL_ALIASES.items():
        if any(re.search(r"(?<![a-z0-9+#])" + re.escape(alias.strip().lower()) + r"(?![a-z0-9+#])", low) for alias in aliases):
            found.append(skill)
    email_match = re.search(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", text, re.I)
    phone_match = re.search(r"(?:\+?\d[\d ()-]{7,}\d)", text)
    education = _section_content(text, SECTION_HEADERS["education"])
    projects = _section_content(text, SECTION_HEADERS["projects"])
    experience = _section_content(text, SECTION_HEADERS["experience"])
    certifications = _section_content(text, SECTION_HEADERS["certifications"])
    sections = {"education": education, "projects": projects, "experience": experience, "certifications": certifications}
    present_sections = [k for k, v in sections.items() if v]
    # Transparent heuristic completeness indicator, not an employability judgment.
    score = round(100 * (0.50 * min(len(found) / 10, 1) + 0.50 * len(present_sections) / 4))
    suggestions = []
    if not education: suggestions.append("Add a clearly labelled Education section with degree, institution, and expected graduation year.")
    if not projects: suggestions.append("Add a Projects section with the problem, your contribution, tools, and measurable outcome.")
    if not experience: suggestions.append("If applicable, add internships, volunteering, freelance work, or relevant practical experience.")
    if not certifications: suggestions.append("Add relevant certifications only if you have earned them; do not list planned certifications as completed.")
    if len(found) < 5: suggestions.append("Include a concise, truthful Technical Skills section with tools you can discuss confidently.")
    if not re.search(r"\b(action|built|developed|implemented|analyzed|improved|created|automated|designed)\b", text, re.I):
        suggestions.append("Start bullet points with clear action verbs and describe the result or impact where you can support it.")
    return {
        "skills": sorted(found), "email": email_match.group(0) if email_match else None,
        "phone_detected": bool(phone_match), "education": education,
        "projects": projects, "experience": experience, "certifications": certifications,
        "sections_found": present_sections, "resume_completeness_score": score,
        "score_note": "Heuristic completeness indicator based on detected skills and sections; not a measure of candidate quality.",
        "suggestions": suggestions,
    }
