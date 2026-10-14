"""Offline, rule-based assistant grounded in the current user's analysis."""

def answer_question(question: str, extracted: dict | None = None, gap: dict | None = None, jobs: list[dict] | None = None) -> str:
    q = (question or "").strip().lower()
    extracted, gap, jobs = extracted or {}, gap or {}, jobs or []
    skills = extracted.get("skills", [])
    if not q:
        return "Ask me about your skills, missing skills, learning roadmap, job matches, or resume improvements."
    if any(word in q for word in ["my skill", "skills do i", "skills detected", "technical skills"]):
        return "Skills detected in your resume: " + (", ".join(skills) if skills else "No supported skills detected yet. Add a clear Technical Skills section and analyze the resume again.")
    if any(word in q for word in ["missing", "gap", "learn first", "priority"]):
        missing = gap.get("missing_skills", [])
        return f"For {gap.get('role', 'your selected role')}, the identified skill gaps are: " + (", ".join(missing) if missing else "No gaps were found among the currently configured roadmap skills. Check the role requirements and keep practicing.")
    if any(word in q for word in ["roadmap", "study plan", "learning plan", "what should i learn"]):
        steps = gap.get("roadmap", [])
        if not steps:
            return "Select a target role in Skill Gap Analysis first. I can then outline a staged learning plan."
        return "Suggested roadmap:\n" + "\n".join(f"{s['step']}. {s['title']}: {s['activity']} Focus skills: {', '.join(s['missing']) if s['missing'] else 'practice and deepen existing skills'}." for s in steps)
    if any(word in q for word in ["match", "job", "role"]):
        if not jobs:
            return "Analyze a resume first so I can summarize the job matches from your current analysis."
        top = jobs[:3]
        return "Top text-similarity matches from your current analysis:\n" + "\n".join(f"• {j['title']} — {j['match_score']}% estimated text similarity" for j in top) + "\nThese scores are not hiring probabilities."
    if any(word in q for word in ["resume", "improve", "cv"]):
        suggestions = extracted.get("suggestions", [])
        return "Resume improvement ideas:\n" + ("\n".join(f"• {s}" for s in suggestions) if suggestions else "Use clear headings, concise action-led bullets, and truthful outcomes you can explain in an interview.")
    if any(word in q for word in ["interview", "prepare"]):
        role = gap.get("role", "your target role")
        return f"For {role}, practice explaining one project end-to-end: problem, your contribution, tools, design choices, testing, limitations, and what you would improve. Also practice fundamentals listed in your roadmap and prepare examples for each skill you claim."
    return "I work offline using rule-based guidance. Try asking: 'What skills were detected?', 'What skills am I missing?', 'Show my roadmap', 'How can I improve my resume?', or 'Which jobs match me?'"
