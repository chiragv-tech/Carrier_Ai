from core.skill_analyzer import analyze_gap

def test_gap_and_roadmap_are_generated():
    result = analyze_gap(["Python", "Git"], "Python Developer")
    assert result["coverage"] > 0
    assert "SQL" in result["missing_skills"]
    assert len(result["roadmap"]) >= 2
