from __future__ import annotations
import json
from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st

from core import database
from core.auth import login_user, register_user
from core.resume_parser import extract_pdf_text, analyze_resume_text
from core.ml_matcher import match_jobs, explain_score
from core.skill_analyzer import analyze_gap, ROLE_PATHS
from core.career_assistant import answer_question
from core.reports import analysis_to_csv, analysis_to_pdf
from ui.styles import inject_css, metric_card
from ui.components import section_heading

ROOT = Path(__file__).resolve().parent
JOBS_PATH = ROOT / "data" / "jobs.json"
ROLES = list(ROLE_PATHS.keys())

st.set_page_config(page_title="CareerAI | Career Intelligence", page_icon="🎯", layout="wide", initial_sidebar_state="expanded")
inject_css()
database.init_db()

@st.cache_data
def load_jobs() -> list[dict]:
    with JOBS_PATH.open("r", encoding="utf-8") as handle:
        return json.load(handle)

JOBS = load_jobs()
for key, default in {"user": None, "analysis": None, "gap_role": ROLES[0], "chat_history": []}.items():
    if key not in st.session_state:
        st.session_state[key] = default


def navigate_to(page_name: str) -> None:
    """Update navigation state in a widget callback before the next rerun."""
    st.session_state.page = page_name
    st.session_state.page_radio = page_name


def open_roadmap(role_name: str) -> None:
    """Store the selected target role and navigate to its roadmap."""
    st.session_state.gap_role = role_name
    navigate_to("Skill Gap & Roadmap")


def logout_user() -> None:
    """Clear the current session in a button callback."""
    st.session_state.user = None
    st.session_state.analysis = None
    st.session_state.chat_history = []
    st.session_state.page = "Dashboard"
    st.session_state.page_radio = "Dashboard"


def show_auth() -> None:
    st.markdown('<div class="hero"><div class="eyebrow">CAREER INTELLIGENCE, BUILT AROUND YOU</div><h1>Make your next career move<br>with more clarity.</h1><p>Understand your resume, discover relevant roles, and turn skill gaps into a practical learning plan — all on your device.</p></div>', unsafe_allow_html=True)
    left, right = st.columns([1.1, 0.9], gap="large")
    with left:
        section_heading("Your career workspace", "A practical toolkit for students and early-career developers.")
        st.markdown("- **Resume intelligence** — extract skills and resume sections from a PDF.\n- **Job matching** — compare your resume with realistic sample roles.\n- **Career roadmap** — focus on skills that matter for your chosen direction.\n- **Private local storage** — accounts and saved analyses live in a local SQLite database.")
        st.info("CareerAI uses offline ML and rule-based guidance. It does not require a paid API or promise hiring outcomes.")
    with right:
        login_tab, register_tab = st.tabs(["Sign in", "Create account"])
        with login_tab:
            with st.form("login_form"):
                email = st.text_input("Email", placeholder="you@example.com")
                password = st.text_input("Password", type="password")
                submitted = st.form_submit_button("Sign in", type="primary", use_container_width=True)
            if submitted:
                ok, message, user = login_user(email, password)
                if ok:
                    st.session_state.user = user
                    st.session_state.page = "Dashboard"
                    st.session_state.page_radio = "Dashboard"
                    st.session_state.chat_history = []
                    st.rerun()
                st.error(message)
        with register_tab:
            with st.form("register_form"):
                full_name = st.text_input("Full name")
                new_email = st.text_input("Email address", placeholder="you@example.com")
                new_password = st.text_input("Password", type="password", help="Use at least 8 characters.")
                confirm_password = st.text_input("Confirm password", type="password")
                submitted = st.form_submit_button("Create account", type="primary", use_container_width=True)
            if submitted:
                if new_password != confirm_password:
                    st.error("Passwords do not match.")
                else:
                    ok, message, _ = register_user(full_name, new_email, new_password)
                    if ok:
                        st.success(message + " Use the Sign in tab to continue.")
                    else:
                        st.error(message)


def current_analysis() -> dict | None:
    return st.session_state.get("analysis")


def require_analysis() -> dict | None:
    analysis = current_analysis()
    if not analysis:
        st.warning("Analyze a resume first. Open **Resume Analyzer** from the sidebar to get started.")
        return None
    return analysis


def render_dashboard() -> None:
    st.markdown('<div class="hero"><div class="eyebrow">YOUR CAREER OVERVIEW</div><h1>Small steps. Stronger opportunities.</h1><p>Turn your resume into a practical view of your skills, relevant sample roles, and next learning priorities.</p></div>', unsafe_allow_html=True)
    analysis = current_analysis()
    if not analysis:
        c1, c2 = st.columns([1.3, 1])
        with c1:
            section_heading("Start with your resume", "Your dashboard becomes personalized after your first analysis.")
            st.markdown("1. Upload a text-searchable PDF resume.\n2. Review detected skills and the ranked job matches.\n3. Choose a target role to see skill gaps and a roadmap.")
            st.button(
                "Analyze a resume",
                type="primary",
                on_click=navigate_to,
                args=("Resume Analyzer",),
            )
        with c2:
            section_heading("Included sample roles")
            for job in JOBS:
                st.markdown(f"**{job['title']}**  \n<small>{job['level']} · {job['location']}</small>", unsafe_allow_html=True)
        return
    jobs = analysis.get("job_matches", [])
    skills = analysis.get("skills", [])
    best = jobs[0] if jobs else None
    cols = st.columns(4)
    with cols[0]: metric_card("Resume completeness", f"{analysis.get('resume_completeness_score', 0)}/100", "Heuristic indicator, not candidate quality")
    with cols[1]: metric_card("Skills detected", str(len(skills)), "From resume text")
    with cols[2]: metric_card("Jobs compared", str(len(jobs)), "Sample job database")
    with cols[3]: metric_card("Top similarity", f"{best['match_score']}%" if best else "—", "Text similarity estimate")
    st.write("")
    left, right = st.columns([1.2, 1], gap="large")
    with left:
        section_heading("Job match overview", "Similarity scores compare text; they are not hiring probabilities.")
        if jobs:
            chart_df = pd.DataFrame([{"Role": j["title"], "Text similarity (%)": j["match_score"]} for j in jobs])
            fig = px.bar(chart_df, x="Text similarity (%)", y="Role", orientation="h", text="Text similarity (%)", color="Text similarity (%)", color_continuous_scale="Blues")
            fig.update_layout(height=330, margin=dict(l=8,r=8,t=15,b=8), coloraxis_showscale=False, yaxis={"categoryorder":"total ascending"}, plot_bgcolor="white", paper_bgcolor="white")
            st.plotly_chart(fig, use_container_width=True)
    with right:
        section_heading("Your detected skill set")
        if skills:
            st.markdown(" ".join(f"`{s}`" for s in skills))
            skill_df = pd.DataFrame({"Type": ["Detected skills", "Other skills in current role roadmap"], "Count": [len(skills), max(0, len(analyze_gap(skills, st.session_state.gap_role)["required_skills"]) - len(analyze_gap(skills, st.session_state.gap_role)["matched_skills"]))]})
            fig2 = px.pie(skill_df, names="Type", values="Count", hole=.62)
            fig2.update_layout(height=250, margin=dict(l=0,r=0,t=8,b=8), legend=dict(orientation="h",y=-.1), paper_bgcolor="white")
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("No skills were detected. Check your resume text and headings.")
    section_heading("Recommended next step")
    target = st.selectbox("Choose a target role", ROLES, key="dashboard_role")
    gap = analyze_gap(skills, target)
    st.progress(gap["coverage"] / 100, text=f"Configured roadmap skill coverage: {gap['coverage']}%")
    st.caption("Coverage only checks the skills configured for this role; it is not a complete measure of readiness.")
    if gap["missing_skills"]:
        st.markdown("**Suggested focus:** " + ", ".join(gap["missing_skills"][:6]))
    st.button(
        "Open personalized roadmap",
        type="primary",
        on_click=open_roadmap,
        args=(target,),
        key="open_personalized_roadmap",
    )


def render_resume_analyzer() -> None:
    section_heading("Resume Analyzer", "Upload a PDF resume. Text extraction and analysis run locally.")
    st.caption("Accepted format: PDF · Maximum 10 MB · Text-searchable PDFs work best. Scanned image-only PDFs need OCR first.")
    uploaded = st.file_uploader("Drop your resume here", type=["pdf"], key="resume_upload")
    selected_role = st.selectbox("Primary career goal", ROLES, index=ROLES.index(st.session_state.gap_role) if st.session_state.gap_role in ROLES else 0)
    if st.button("Analyze resume", type="primary", disabled=uploaded is None):
        try:
            with st.spinner("Reading resume and comparing sample jobs..."):
                resume_text = extract_pdf_text(uploaded.getvalue())
                extracted = analyze_resume_text(resume_text)
                matches = match_jobs(resume_text, JOBS)
                gap = analyze_gap(extracted["skills"], selected_role)
                results = {**extracted, "job_matches": matches, "selected_role": selected_role, "skill_gap": gap, "match_explanation": explain_score()}
                analysis_id = database.save_analysis(st.session_state.user["id"], uploaded.name, resume_text, extracted, results)
                results["analysis_id"] = analysis_id
                st.session_state.analysis = {"resume_name": uploaded.name, "resume_text": resume_text, **results}
                st.session_state.gap_role = selected_role
            st.success("Resume analyzed and saved to your account.")
        except ValueError as exc:
            st.error(str(exc))
        except Exception as exc:
            st.error("The analysis could not be completed. Check the PDF and try again.")
            st.exception(exc)
    analysis = current_analysis()
    if analysis:
        st.divider()
        section_heading("Latest analysis", analysis.get("resume_name", "Resume"))
        a, b, c = st.columns(3)
        a.metric("Completeness indicator", f"{analysis.get('resume_completeness_score', 0)}/100")
        b.metric("Detected skills", len(analysis.get("skills", [])))
        c.metric("Job roles compared", len(analysis.get("job_matches", [])))
        st.caption(analysis.get("score_note", ""))
        with st.expander("View extracted resume sections"):
            for label in ["education", "projects", "experience", "certifications"]:
                st.markdown(f"**{label.title()}**")
                st.write(analysis.get(label) or "No clearly labelled section detected.")
        st.markdown("**Detected skills**")
        st.write(", ".join(analysis.get("skills", [])) or "No supported skills detected.")
        st.markdown("**Resume improvement suggestions**")
        for suggestion in analysis.get("suggestions", []): st.markdown(f"- {suggestion}")
        st.markdown("**Ranked job matches**")
        render_job_table(analysis.get("job_matches", []))
        render_downloads(analysis)


def render_job_table(jobs: list[dict]) -> None:
    if not jobs:
        st.info("No job matches available yet."); return
    table = pd.DataFrame([{"Rank": i, "Role": j["title"], "Sample company": j["company"], "Similarity (%)": j["match_score"], "Skill coverage (%)": j["skill_coverage"], "Matched skills": ", ".join(j["matched_skills"]), "Missing skills": ", ".join(j["missing_skills"])} for i, j in enumerate(jobs, 1)])
    st.dataframe(table, use_container_width=True, hide_index=True)
    st.caption(explain_score())


def render_downloads(analysis: dict) -> None:
    report_data = {k: analysis.get(k) for k in ["skills", "suggestions", "resume_completeness_score", "score_note", "job_matches"]}
    c1, c2 = st.columns(2)
    with c1:
        st.download_button("Download PDF report", data=analysis_to_pdf(report_data, analysis.get("resume_name", "Resume")), file_name="careerai_report.pdf", mime="application/pdf", use_container_width=True)
    with c2:
        st.download_button("Download CSV results", data=analysis_to_csv(report_data), file_name="careerai_job_matches.csv", mime="text/csv", use_container_width=True)


def render_job_matcher() -> None:
    section_heading("AI Job Matcher", "Compare the latest analyzed resume against the sample job database.")
    analysis = require_analysis()
    if not analysis: return
    render_job_table(analysis.get("job_matches", []))
    selected = st.selectbox("Inspect a role", [j["title"] for j in analysis.get("job_matches", [])])
    job = next((j for j in analysis["job_matches"] if j["title"] == selected), None)
    if job:
        left, right = st.columns(2)
        with left:
            st.metric("Text similarity estimate", f"{job['match_score']}%")
            st.metric("Configured skill coverage", f"{job['skill_coverage']}%")
            st.write(job["description"])
        with right:
            st.markdown("**Matched skills**")
            st.success(", ".join(job["matched_skills"]) or "No configured skills matched directly.")
            st.markdown("**Skills not detected**")
            st.warning(", ".join(job["missing_skills"]) or "All configured role skills were detected in the resume text.")
    render_downloads(analysis)


def render_skill_gap() -> None:
    section_heading("Skill Gap & Roadmap", "Identify skill gaps for a chosen role and turn them into manageable projects.")
    analysis = require_analysis()
    if not analysis: return
    role = st.selectbox("Target role", ROLES, index=ROLES.index(st.session_state.gap_role) if st.session_state.gap_role in ROLES else 0)
    st.session_state.gap_role = role
    gap = analyze_gap(analysis.get("skills", []), role)
    st.progress(gap["coverage"] / 100, text=f"Configured skill coverage: {gap['coverage']}%")
    st.caption("This compares detected skills against a small, editable role checklist; it is a learning aid, not a formal assessment.")
    c1, c2 = st.columns(2)
    with c1:
        section_heading("Skills already detected")
        if gap["matched_skills"]: st.success(" · ".join(gap["matched_skills"]))
        else: st.write("No skills from this role checklist were detected yet.")
    with c2:
        section_heading("Potential skill gaps")
        if gap["missing_skills"]: st.warning(" · ".join(gap["missing_skills"]))
        else: st.success("No gaps in the configured checklist. Continue with practice and projects.")
    section_heading("Your step-by-step learning roadmap")
    for step in gap["roadmap"]:
        with st.expander(f"Step {step['step']} · {step['title']} — {step['status']}", expanded=step["step"] == 1):
            st.write(step["activity"])
            st.markdown("**Skills to cover:** " + ", ".join(step["skills"]))
            st.markdown("**Not detected yet:** " + (", ".join(step["missing"]) or "None in this checklist; practice and build depth."))
    if st.button("Save this roadmap to current analysis"):
        # Save an updated snapshot owned by the current account.
        results = {k: analysis.get(k) for k in ["skills", "suggestions", "resume_completeness_score", "score_note", "job_matches"]}
        results["skill_gap"] = gap; results["selected_role"] = role
        new_id = database.save_analysis(st.session_state.user["id"], analysis.get("resume_name", "Resume"), analysis.get("resume_text", ""), {k: analysis.get(k) for k in ["skills", "suggestions", "resume_completeness_score", "score_note"]}, results)
        st.success(f"Roadmap snapshot saved (analysis #{new_id}).")


def render_assistant() -> None:
    section_heading("AI Career Assistant", "Offline rule-based assistant using your latest resume analysis and target role.")
    analysis = current_analysis()
    if not analysis:
        st.info("Analyze a resume first for personalized answers. You can still ask general career questions.")
    if "chat_history" not in st.session_state: st.session_state.chat_history = []
    for item in st.session_state.chat_history:
        with st.chat_message(item["role"]): st.markdown(item["content"])
    prompt = st.chat_input("Ask about your skills, job matches, or roadmap...")
    if prompt:
        st.session_state.chat_history.append({"role":"user", "content":prompt})
        gap = analyze_gap(analysis.get("skills", []), st.session_state.gap_role) if analysis else {}
        response = answer_question(prompt, analysis, gap, analysis.get("job_matches", []) if analysis else [])
        st.session_state.chat_history.append({"role":"assistant", "content":response})
        st.rerun()
    with st.expander("Try a sample question"):
        for example in ["What skills were detected?", "What skills am I missing?", "Show my roadmap", "How can I improve my resume?", "Which jobs match me?"]:
            if st.button(example, key="sample_" + example):
                st.session_state.chat_history.append({"role":"user", "content":example})
                gap = analyze_gap(analysis.get("skills", []), st.session_state.gap_role) if analysis else {}
                response = answer_question(example, analysis, gap, analysis.get("job_matches", []) if analysis else [])
                st.session_state.chat_history.append({"role":"assistant", "content":response})
                st.rerun()


def render_saved_analyses() -> None:
    section_heading("Saved analyses", "Only records belonging to your signed-in account are listed here.")
    records = database.list_analyses(st.session_state.user["id"])
    if not records:
        st.info("No saved analyses yet. Upload a resume to create one."); return
    frame = pd.DataFrame([{"Analysis ID": r["id"], "Resume file": r["resume_name"], "Saved at": r["created_at"]} for r in records])
    st.dataframe(frame, use_container_width=True, hide_index=True)
    options = {f"#{r['id']} · {r['resume_name']} · {r['created_at']}": r["id"] for r in records}
    chosen_label = st.selectbox("Open a saved analysis", list(options))
    chosen_id = options[chosen_label]
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Load selected analysis", type="primary"):
            record = database.get_analysis(st.session_state.user["id"], chosen_id)
            if record:
                st.session_state.analysis = {"analysis_id": record["id"], "resume_name": record["resume_name"], "resume_text": record["resume_text"], **record["extracted"], **record["results"]}
                st.session_state.gap_role = st.session_state.analysis.get("selected_role", ROLES[0])
                st.success("Analysis loaded into your workspace."); st.rerun()
            else: st.error("That saved analysis could not be found for your account.")
    with c2:
        if st.button("Delete selected analysis"):
            if database.delete_analysis(st.session_state.user["id"], chosen_id):
                st.success("Saved analysis deleted."); st.rerun()
            else: st.error("Could not delete that analysis.")


def render_job_database() -> None:
    section_heading("Sample Job Database", "These fictional sample listings demonstrate the matching workflow; they are not live vacancies.")
    search = st.text_input("Search roles or skills", placeholder="e.g. Python, data, API")
    jobs = [j for j in JOBS if not search or search.lower() in (j["title"] + " " + j["description"] + " " + " ".join(j["skills"])).lower()]
    for job in jobs:
        with st.expander(f"{job['title']} · {job['level']} · {job['location']}"):
            st.markdown(f"**Sample organization:** {job['company']}")
            st.write(job["description"])
            st.markdown("**Skills:** " + ", ".join(job["skills"]))
    st.caption("To add a role, append an object to data/jobs.json with a unique id, title, company, level, location, description, and skills list. Restart the app after editing.")


def render_project_guide() -> None:
    section_heading("How CareerAI works", "A beginner-friendly technical overview.")
    with st.expander("1. Resume parsing", expanded=True):
        st.write("PyMuPDF reads selectable text from PDF pages. A small rule-based extractor detects common skill terms and looks for labelled Education, Projects, Experience, and Certifications sections. It does not reliably understand every resume layout, and image-only PDFs need OCR.")
    with st.expander("2. TF-IDF and cosine similarity"):
        st.write("TF-IDF assigns higher weight to terms that are useful in a document and less common across the compared documents. CareerAI vectorizes the resume and each sample job description, then computes cosine similarity between vectors. Results are ranked by similarity and shown as estimates, not hiring probabilities.")
        st.code("cosine_similarity(A, B) = (A · B) / (||A|| × ||B||)", language="text")
    with st.expander("3. Skill gaps and roadmaps"):
        st.write("A configurable checklist is maintained for each sample career path. Skills detected in the resume are compared with that checklist. Missing items are paired with staged practice activities. This is a transparent rule-based feature, not a trained predictive model.")
    with st.expander("4. SQLite and account separation"):
        st.write("SQLite stores user email, display name, salted PBKDF2 password hash, and saved analyses. Database functions require the authenticated user ID for reading or deleting analyses. Passwords are never stored in plain text. This is a local demo; a public deployment would need additional security review and controls.")
    with st.expander("5. Limitations and responsible use"):
        st.write("The sample jobs are fictional; match results depend on wording and the configured skill vocabulary. The completeness indicator is a heuristic, not a judgement of a person. Review suggestions critically, verify role requirements, and never add skills or achievements you do not have.")


if not st.session_state.user:
    show_auth()
else:
    with st.sidebar:
        st.markdown("# 🎯 CareerAI")
        st.caption("AI Career Intelligence")
        st.markdown(f"Signed in as **{st.session_state.user['full_name']}**")
        st.divider()
        pages = ["Dashboard", "Resume Analyzer", "AI Job Matcher", "Skill Gap & Roadmap", "Career Assistant", "Saved Analyses", "Sample Job Database", "Project Guide"]
        if "page" not in st.session_state: st.session_state.page = "Dashboard"
        selected_page = st.radio("Workspace", pages, key="page_radio", index=pages.index(st.session_state.page) if st.session_state.page in pages else 0, label_visibility="collapsed")
        st.session_state.page = selected_page
        st.divider()
        if st.session_state.analysis:
            st.caption("Latest resume")
            st.write(st.session_state.analysis.get("resume_name", "Resume"))
        st.button("Log out", on_click=logout_user, use_container_width=True)
    page = st.session_state.page
    if page == "Dashboard": render_dashboard()
    elif page == "Resume Analyzer": render_resume_analyzer()
    elif page == "AI Job Matcher": render_job_matcher()
    elif page == "Skill Gap & Roadmap": render_skill_gap()
    elif page == "Career Assistant": render_assistant()
    elif page == "Saved Analyses": render_saved_analyses()
    elif page == "Sample Job Database": render_job_database()
    elif page == "Project Guide": render_project_guide()
    st.divider()
    st.caption("CareerAI · Local-first educational prototype · Match scores are text-similarity estimates, not hiring probabilities.")
