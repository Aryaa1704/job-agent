import json
from ai.matcher import analyze_job
from ai.resume_tailor import tailor_resume

with open("data/profile.json", "r") as f:
    profile = json.load(f)

jd = """
Software Engineer - Python
Company: TechCorp India
Location: Delhi / Remote

We are looking for a Python developer with:
- 1-2 years experience
- Strong Python and Django skills
- REST API development
- PostgreSQL knowledge
- Git version control
- AWS basics preferred

Salary: 8-12 LPA
"""

print("Analyzing job...")
result = analyze_job(jd, profile)
print("\n=== MATCH RESULT ===")
print(f"Score: {result['match_score']}%")
print(f"Recommendation: {result['recommendation']}")
print(f"Reason: {result['reason']}")
print(f"Matched: {result['matched_skills']}")
print(f"Missing: {result['missing_skills']}")

if result['missing_info_needed']:
    print("\nQuestions for you:")
    for q in result['missing_info_needed']:
        print(f"  -> {q['question']}")

print("\nGenerating tailored resume...")
resume = tailor_resume(jd, profile)
print("\n=== TAILORED RESUME ===")
print(resume)
