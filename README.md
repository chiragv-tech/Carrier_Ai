# CareerAI — AI Career Intelligence Platform

CareerAI is a local-first Streamlit application for resume text extraction, content-based job matching, skill-gap analysis, learning roadmaps, an offline rule-based career assistant, user accounts, saved analyses, interactive charts, and PDF/CSV exports.

## Features

- PDF resume extraction with PyMuPDF and graceful validation errors.
- Rule-based extraction of common skills and labelled resume sections.
- TF-IDF + cosine-similarity ranking against five fictional sample job descriptions.
- Skill checklist coverage, missing skills, and staged role roadmaps.
- Interactive Plotly dashboard.
- Registration, login, salted PBKDF2 password hashes, and per-user saved analysis access in SQLite.
- Rule-based assistant that works without an LLM or paid API.
- PDF and CSV report downloads.
- Automated tests with pytest.

## Requirements

- Windows 10/11 (or another OS with Python support)
- Python 3.11 recommended
- Internet is not required at runtime for the ML and core app features. Google Fonts are referenced by the optional UI stylesheet; if offline, the browser falls back to local sans-serif fonts.

## Windows PowerShell installation

Open PowerShell in the folder where you want the project and run:

```powershell
# 1. Go to the extracted project folder
cd .\CareerAI

# 2. Create a virtual environment
py -3.11 -m venv .venv

# 3. Activate it
.\.venv\Scripts\Activate.ps1

# If PowerShell blocks activation for this terminal only, use:
# Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
# .\.venv\Scripts\Activate.ps1

# 4. Upgrade pip and install dependencies
python -m pip install --upgrade pip
pip install -r requirements.txt

# 5. Run the automated tests
python -m pytest -q

# 6. Launch the app
python -m streamlit run app.py
```

Streamlit prints a local URL, normally `http://localhost:8501`. Open it in your browser. The SQLite database (`careerai.db`) is created automatically in the project directory.

### If Python is already installed

Use `py --version` to check. Python 3.11 is recommended. If `py -3.11` is not found, install Python 3.11 and enable the Python Launcher, then repeat the commands above.

## First-use guide

1. Select **Create account** and register with a valid email and a password of at least eight characters.
2. Sign in.
3. Open **Resume Analyzer** and upload a text-searchable PDF resume.
4. Select a career goal and click **Analyze resume**.
5. Review extracted skills, section detections, suggestions, and ranked roles.
6. Download PDF and CSV reports.
7. Open **Skill Gap & Roadmap**, choose a role, and inspect the learning steps.
8. Ask the **Career Assistant** about detected skills, missing skills, the roadmap, resume improvements, or job matches.
9. Open **Saved Analyses** to load or delete account-owned records.

## Test instructions

From the project root, with the virtual environment activated:

```powershell
python -m pytest -q
```

The tests cover password hashing, skill extraction, invalid PDF handling, relevant-job ranking, empty input, and roadmap generation. Manual end-to-end checks are in `docs/PROJECT_REPORT.md`.

## Adding sample job roles

Edit `data/jobs.json` and add an object with these fields:

```json
{
  "id": "unique-role-id",
  "title": "Example Role",
  "company": "Example Company (Sample)",
  "level": "Entry-level",
  "location": "Remote / India",
  "description": "A realistic description with responsibilities and tools.",
  "skills": ["Python", "SQL", "Git"]
}
```

Keep `id` unique, ensure JSON commas and quotation marks are valid, then restart Streamlit. Skill matching and roadmap requirements are configured separately in `core/skill_analyzer.py` and `core/resume_parser.py`.

## Architecture

- `app.py`: navigation and page composition.
- `core/database.py`: SQLite schema and user-scoped persistence functions.
- `core/auth.py`: registration validation, PBKDF2 password hashes, login.
- `core/resume_parser.py`: PDF extraction and heuristic parsing.
- `core/ml_matcher.py`: TF-IDF vectorization and cosine similarity.
- `core/skill_analyzer.py`: skill checklist comparison and roadmaps.
- `core/career_assistant.py`: deterministic offline assistant.
- `core/reports.py`: report generation.
- `ui/`: styling and reusable components.
- `tests/`: automated unit tests.

## Important limitations

- Sample job listings are fictional and are not live vacancies.
- Similarity scores measure text similarity, not hiring probability, job suitability, or the chance of receiving an offer.
- Resume parsing is heuristic. Layout variations, unusual skill wording, and scanned PDFs can reduce extraction quality.
- The resume completeness indicator is a transparent heuristic, not a measure of a person's ability or employability.
- This is an internship/demo prototype. Before public deployment, add HTTPS, CSRF/session protections, rate limiting, secure secret management, privacy/retention controls, database backups, security review, and production-grade authorization testing.
- Avoid uploading sensitive documents to shared computers. Resume text is stored in the local SQLite database when an analysis is saved.
