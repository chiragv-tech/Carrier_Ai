import pytest
from core.resume_parser import extract_pdf_text, analyze_resume_text

def test_rejects_non_pdf():
    with pytest.raises(ValueError, match="valid PDF"):
        extract_pdf_text(b"not a pdf")

def test_detects_skills_and_sections():
    text = """EDUCATION\nB.Tech Computer Science\nPROJECTS\nBuilt a Python Streamlit dashboard using pandas and SQL.\nEXPERIENCE\nInternship developing REST API with Git and testing.\nCERTIFICATIONS\nIntro to Python certificate"""
    result = analyze_resume_text(text)
    assert "python" in result["skills"]
    assert "sql" in result["skills"]
    assert "projects" in result["sections_found"]
    assert result["resume_completeness_score"] >= 50
