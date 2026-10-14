"""Rule-based skill-gap analysis and role-specific learning roadmaps."""
from __future__ import annotations
ROLE_PATHS = {
    "Python Developer": [
        ("Python foundations", ["Python", "OOP", "Debugging"], "Review functions, collections, exceptions, modules, and object-oriented programming."),
        ("Work with data and APIs", ["SQL", "REST API", "FastAPI"], "Build a small API and connect it to a relational database."),
        ("Quality and delivery", ["Git", "Testing"], "Add unit tests, version control, a README, and deployment instructions."),
    ],
    "Data Analyst": [
        ("Data handling", ["Python", "Pandas", "SQL", "Data Cleaning"], "Clean a public dataset and write reusable analysis queries."),
        ("Statistics and insight", ["Statistics", "Excel"], "Summarize distributions, uncertainty, and meaningful comparisons."),
        ("Visualization and storytelling", ["Data Visualization", "Plotly"], "Create an interactive dashboard and explain three evidence-backed insights."),
    ],
    "Machine Learning Engineer": [
        ("Python data stack", ["Python", "NumPy", "Pandas"], "Practice preprocessing and exploratory analysis on a documented dataset."),
        ("Core machine learning", ["Scikit-learn", "Statistics", "Feature Engineering"], "Train baseline models and compare appropriate validation strategies."),
        ("Evaluation and reproducibility", ["Model Evaluation", "Git", "Machine Learning"], "Report precision, recall, F1, limitations, and reproducible setup steps."),
    ],
    "Web Developer": [
        ("Frontend foundations", ["HTML", "CSS", "JavaScript"], "Build an accessible responsive page with form validation."),
        ("Integration", ["REST API", "Git"], "Connect the interface to an API and handle loading and error states."),
        ("Modern UI quality", ["Responsive Design", "Testing"], "Test common viewport sizes and document usability decisions."),
    ],
    "Software Engineer": [
        ("Programming fundamentals", ["Python", "Java", "OOP"], "Choose one primary language and implement small maintainable programs."),
        ("Problem solving", ["Data Structures", "Algorithms"], "Practice arrays, hash maps, stacks, trees, searching, and sorting."),
        ("Engineering practice", ["SQL", "Git", "Testing"], "Build a small application with tests, database persistence, and clear documentation."),
    ],
}

def analyze_gap(existing_skills: list[str], role: str) -> dict:
    existing = {s.casefold() for s in existing_skills}
    path = ROLE_PATHS.get(role, ROLE_PATHS["Software Engineer"])
    required = []
    for _, skills, _ in path:
        required.extend(skills)
    # Keep role requirements ordered while removing duplicates.
    required = list(dict.fromkeys(required))
    matched = [s for s in required if s.casefold() in existing]
    missing = [s for s in required if s.casefold() not in existing]
    steps = []
    for index, (title, skills, activity) in enumerate(path, 1):
        step_missing = [s for s in skills if s.casefold() not in existing]
        steps.append({"step": index, "title": title, "skills": skills, "missing": step_missing,
                      "activity": activity, "status": "Review / practice" if not step_missing else "Learning priority"})
    return {"role": role, "required_skills": required, "matched_skills": matched, "missing_skills": missing,
            "coverage": round(100 * len(matched) / max(1, len(required)), 1), "roadmap": steps}
