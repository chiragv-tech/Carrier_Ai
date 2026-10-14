"""CSV and PDF export helpers."""
from __future__ import annotations
from io import BytesIO
import csv
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

def analysis_to_csv(results: dict) -> bytes:
    output = BytesIO()
    import io
    text_buffer = io.StringIO(newline="")
    writer = csv.writer(text_buffer)
    writer.writerow(["CareerAI Career Analysis"])
    writer.writerow(["Resume completeness indicator", results.get("resume_completeness_score", "")])
    writer.writerow(["Note", results.get("score_note", "")])
    writer.writerow([])
    writer.writerow(["Rank", "Job title", "Company (sample)", "Match similarity (%)", "Skill coverage (%)", "Matched skills", "Missing skills"])
    for i, job in enumerate(results.get("job_matches", []), 1):
        writer.writerow([i, job.get("title", ""), job.get("company", ""), job.get("match_score", 0), job.get("skill_coverage", 0), ", ".join(job.get("matched_skills", [])), ", ".join(job.get("missing_skills", []))])
    writer.writerow([])
    writer.writerow(["Detected skills", ", ".join(results.get("skills", []))])
    writer.writerow(["Resume suggestions", " | ".join(results.get("suggestions", []))])
    return text_buffer.getvalue().encode("utf-8-sig")

def analysis_to_pdf(results: dict, resume_name: str = "Resume") -> bytes:
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=18*mm, leftMargin=18*mm, topMargin=17*mm, bottomMargin=17*mm)
    styles = getSampleStyleSheet()
    story = [Paragraph("CareerAI — Career Analysis Report", styles["Title"]), Spacer(1, 5*mm),
             Paragraph(f"Resume: {resume_name}", styles["Normal"]), Spacer(1, 3*mm),
             Paragraph(f"Resume completeness indicator: {results.get('resume_completeness_score', 0)}/100", styles["Heading2"]),
             Paragraph(results.get("score_note", ""), styles["BodyText"]), Spacer(1, 4*mm),
             Paragraph("Detected skills", styles["Heading2"]),
             Paragraph(", ".join(results.get("skills", [])) or "No skills detected", styles["BodyText"]), Spacer(1, 4*mm),
             Paragraph("Ranked job matches", styles["Heading2"])]
    data = [["Role", "Similarity", "Coverage"]]
    for job in results.get("job_matches", []):
        data.append([job.get("title", ""), f"{job.get('match_score', 0)}%", f"{job.get('skill_coverage', 0)}%"])
    table = Table(data, colWidths=[90*mm, 35*mm, 35*mm], repeatRows=1)
    table.setStyle(TableStyle([("BACKGROUND", (0,0), (-1,0), colors.HexColor("#202B5B")), ("TEXTCOLOR", (0,0), (-1,0), colors.white), ("GRID", (0,0), (-1,-1), 0.4, colors.HexColor("#D7DCE5")), ("PADDING", (0,0), (-1,-1), 6), ("VALIGN", (0,0), (-1,-1), "TOP")]))
    story.extend([table, Spacer(1, 4*mm), Paragraph("Resume improvement suggestions", styles["Heading2"])])
    suggestions = results.get("suggestions", []) or ["Continue tailoring your resume to each role and describe projects truthfully."]
    for suggestion in suggestions:
        story.append(Paragraph("• " + suggestion.replace("&", "&amp;"), styles["BodyText"]))
        story.append(Spacer(1, 2*mm))
    story.extend([Spacer(1, 4*mm), Paragraph("Interpretation note", styles["Heading2"]), Paragraph("Job match values are TF-IDF cosine text-similarity estimates, not probabilities of getting hired. Sample roles are illustrative. This report is educational guidance and does not guarantee recruitment outcomes.", styles["BodyText"])])
    doc.build(story)
    return buffer.getvalue()
