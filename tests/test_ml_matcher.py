from core.ml_matcher import match_jobs

def test_matching_ranks_relevant_job_higher():
    jobs = [
        {"title":"Python Developer", "description":"Python REST API SQL backend development", "skills":["Python", "SQL"]},
        {"title":"Web Designer", "description":"CSS layout visual design accessibility", "skills":["CSS", "HTML"]},
    ]
    result = match_jobs("Python developer building REST API in Python with SQL database", jobs)
    assert result[0]["title"] == "Python Developer"
    assert 0 <= result[0]["match_score"] <= 100
    assert "Python" in result[0]["matched_skills"]

def test_empty_resume_returns_empty():
    assert match_jobs("", [{"title":"Test", "description":"sample", "skills":[]}]) == []
