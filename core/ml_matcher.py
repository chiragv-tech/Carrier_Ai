"""Content-based job matching using TF-IDF and cosine similarity."""
from __future__ import annotations
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def _job_text(job: dict) -> str:
    return " ".join([job.get("title", ""), job.get("description", ""), " ".join(job.get("skills", []))])

def match_jobs(resume_text: str, jobs: list[dict]) -> list[dict]:
    if not resume_text or not resume_text.strip() or not jobs:
        return []
    documents = [resume_text] + [_job_text(job) for job in jobs]
    vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2), sublinear_tf=True)
    try:
        matrix = vectorizer.fit_transform(documents)
    except ValueError:  # e.g. text contains only stop words
        return [{**job, "match_score": 0.0, "matched_skills": [], "missing_skills": list(job.get("skills", []))} for job in jobs]
    similarities = cosine_similarity(matrix[0:1], matrix[1:]).flatten()
    resume_low = resume_text.lower()
    output = []
    for job, similarity in zip(jobs, similarities):
        matched, missing = [], []
        for skill in job.get("skills", []):
            pattern = r"(?<![a-z0-9+#])" + re.escape(skill.lower()) + r"(?![a-z0-9+#])"
            (matched if re.search(pattern, resume_low) else missing).append(skill)
        output.append({**job, "match_score": round(float(similarity) * 100, 1),
                       "matched_skills": matched, "missing_skills": missing,
                       "skill_coverage": round(100 * len(matched) / max(1, len(job.get("skills", []))), 1)})
    return sorted(output, key=lambda item: item["match_score"], reverse=True)

def explain_score() -> str:
    return ("The estimate compares TF-IDF-weighted terms in the resume and job description using cosine similarity. "
            "It is a text-similarity estimate, not a probability of getting hired; wording, resume formatting, and the sample job dataset affect it.")
