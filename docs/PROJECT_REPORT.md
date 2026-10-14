# CareerAI — AI Career Intelligence Platform

## 1. Abstract
CareerAI is a local-first career guidance prototype that helps students inspect resume content, compare resumes with sample job descriptions, identify skills that are not detected for a selected role, and plan learning activities. It combines text extraction, classical information retrieval, rule-based logic, local persistence, and interactive visualization. The application is built with Streamlit and Python, uses scikit-learn for TF-IDF and cosine similarity, PyMuPDF for PDF text extraction, SQLite for persistence, Plotly for charts, and ReportLab/pandas-compatible exports for reports. It does not depend on paid AI APIs.

## 2. Problem statement
Students may find it difficult to translate a resume into concrete role targets and learning priorities. CareerAI provides a structured starting point by comparing resume wording with a small role dataset and displaying detected and missing skills. It is decision support, not a recruiter or a hiring prediction system.

## 3. Objectives
- Extract text from text-searchable PDF resumes.
- Detect common skills and selected resume sections.
- Rank sample job descriptions by text similarity.
- Compare detected skills with a role-specific checklist.
- Suggest a staged learning roadmap and resume improvements.
- Save account-specific analyses and export reports.
- Provide career guidance without requiring a remote LLM.

## 4. Technology stack
| Layer | Technology | Purpose |
|---|---|---|
| UI | Streamlit + custom CSS | Pages, forms, navigation, responsive layout |
| Language | Python | Application and feature logic |
| ML / text | scikit-learn | TF-IDF vectors and cosine similarity |
| PDF | PyMuPDF | Local PDF text extraction |
| Storage | SQLite | Users and saved analyses |
| Charts | Plotly | Interactive match and skill charts |
| Reports | ReportLab + CSV | Downloadable reports |
| Tests | pytest | Automated unit tests |

## 5. Architecture and workflow
1. A user registers and signs in. The password is converted into a salted PBKDF2 hash; the original password is not stored.
2. The user uploads a PDF. PyMuPDF extracts selectable text and validation checks reject unsupported or unreadable files.
3. A rule-based parser looks for common skill names and labelled sections.
4. The ML matcher vectorizes the resume and each job document using TF-IDF and calculates cosine similarity.
5. Jobs are sorted by similarity. A separate explicit skill checklist identifies matched and missing role skills.
6. Roadmap rules group required skills into learning stages and propose practice activities.
7. The assistant maps common question intents to answers based on the current analysis.
8. The user can save analysis records to SQLite and export reports to PDF or CSV.

## 6. ML algorithm explanation
TF-IDF means Term Frequency–Inverse Document Frequency. Term frequency reflects how often a term occurs in a document; inverse document frequency reduces the influence of terms common across the collection. `TfidfVectorizer` transforms the resume and job descriptions into weighted numeric vectors. Cosine similarity measures the angle between two vectors:

`similarity(A, B) = (A · B) / (||A|| × ||B||)`

A larger cosine similarity indicates more overlap in the weighted wording of the two documents. CareerAI multiplies the result by 100 for display and sorts the roles. This score is not calibrated, not a probability, and not a prediction of hiring success. Resume wording, document length, dataset design, and vectorizer settings can affect results.

## 7. Resume analysis logic
PyMuPDF reads text from each PDF page. The extractor detects terms from a configurable vocabulary and looks for common section headings. The completeness indicator combines detected skill count with the presence of four labelled sections. This is a simple heuristic used to demonstrate a dashboard metric; it does not judge candidate quality. A production parser would need layout-aware extraction, OCR, broader aliases, and validation against representative resumes.

## 8. Database design
### Users
- `id`: primary key
- `email`: unique email address
- `full_name`: display name
- `password_hash`: salted PBKDF2 hash
- `created_at`: creation timestamp

### Analyses
- `id`: primary key
- `user_id`: foreign key to users
- `resume_name`: uploaded file name
- `resume_text`: extracted resume text
- `extracted_json`: structured extraction result
- `results_json`: job matches and analysis results
- `created_at`: save timestamp

Analysis read/delete operations filter on both the record ID and authenticated user ID. This provides application-level account separation for the local prototype; production deployment still requires security review.

## 9. Functional modules
- Authentication and user session.
- Resume PDF upload and parsing.
- Job similarity matching and ranking.
- Skill gap analysis and role-specific roadmap.
- Dashboard charts and key metrics.
- Rule-based career assistant.
- Saved analysis management.
- PDF and CSV downloads.
- Sample job database and project guide.

## 10. Testing plan
Run `python -m pytest -q` from the project root. Unit tests cover password hash verification, invalid PDF rejection, skill/section extraction, matching relevance, empty resume behavior, and roadmap generation. Also perform the manual checks below:

| Test | Steps | Expected result |
|---|---|---|
| Registration | Create account with valid data | Account created; password hash stored |
| Validation | Use short password or invalid email | Helpful validation message |
| Login | Correct and incorrect password | Correct login succeeds; wrong login is rejected |
| PDF validation | Upload a non-PDF renamed as PDF | Clear validation error |
| Resume parsing | Upload text-searchable resume PDF | Text, skills, sections, and suggestions displayed |
| Job matching | Analyze a resume with Python/SQL content | Relevant sample roles ranked by actual text similarity |
| Skill gap | Choose Machine Learning Engineer | Detected/missing skills and roadmap shown |
| Assistant | Ask “What skills were detected?” | Answer uses current analysis |
| Reports | Download PDF and CSV | Files open and contain analysis data |
| Saved data | Save, load, and delete analysis | Current user's records are available and deletable |
| Account separation | Sign in as another account | First user's saved records are not listed |
| Job database | Search for “Python” | Relevant sample role entries shown |

## 11. Known limitations
- The job dataset is illustrative and not connected to a live job board.
- Skill extraction uses a fixed vocabulary and simple string matching.
- Scanned image PDFs are not OCR-processed.
- Roadmaps use hand-written rules rather than a trained recommender model.
- The assistant is intent-based and is not a generative language model.
- Local SQLite and Streamlit authentication are suitable for a demonstration, not a hardened public service.

## 12. Future enhancements
- OCR for scanned documents.
- Semantic embeddings and evaluation against labelled matching examples.
- Admin interface for job data and skill vocabulary management.
- More roles, skill synonyms, and user-editable extracted skills.
- Privacy controls to delete all account data and set retention periods.
- Integration with verified job feeds, only after respecting their terms and data quality.
- Production deployment with robust authentication, secure sessions, audit logs, and automated tests.

## 13. Conclusion
CareerAI demonstrates an end-to-end AI/ML-flavoured application that combines classical text similarity with transparent rules, a local database, interactive UI, and downloadable reports. Its design emphasizes explainability and clearly states the limitations of similarity scores and heuristic extraction.
