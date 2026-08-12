import os
import json
import re
from groq import Groq

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def generate_cover_letter(jd: str, profile: dict, tone: str = "professional") -> str:
    personal = profile.get("personal", profile)
    skills = profile.get("skills", [])
    if isinstance(skills, dict):
        all_skills = []
        for v in skills.values():
            if isinstance(v, list): all_skills.extend(v)
        skills = all_skills

    prompt = f"""Write a compelling cover letter.
CANDIDATE: {personal.get('name','')} | Skills: {', '.join(skills[:10])}
JOB: {jd}
TONE: {tone}
RULES: 3 paragraphs, under 300 words, use JD keywords, real data only, professional sign-off.
Write only the cover letter, nothing else."""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=800, temperature=0.4
    )
    return response.choices[0].message.content


def generate_apply_package(jd: str, profile: dict) -> dict:
    personal = profile.get("personal", profile)
    skills = profile.get("skills", [])
    if isinstance(skills, dict):
        all_skills = []
        for v in skills.values():
            if isinstance(v, list): all_skills.extend(v)
        skills = all_skills

    prompt = f"""Extract job info and create apply package.
JOB DESCRIPTION: {jd}
CANDIDATE: Name={personal.get('name','')}, Email={personal.get('email','')}, Phone={personal.get('phone','')}, Location={personal.get('location','')}, LinkedIn={personal.get('linkedin','')}, GitHub={personal.get('github','')}, Skills={', '.join(skills[:15])}

Return ONLY valid JSON:
{{
  "company_name": "from JD",
  "job_title": "from JD",
  "apply_url": "direct link if in JD else empty",
  "email_to_apply": "hr email if in JD else empty",
  "location": "job location",
  "job_type": "Full-time/Internship/Contract",
  "salary": "if mentioned else Not mentioned",
  "experience_required": "X years or Fresher",
  "key_requirements": ["req1", "req2", "req3", "req4", "req5"],
  "form_fill_data": {{
    "full_name": "{personal.get('name','')}",
    "email": "{personal.get('email','')}",
    "phone": "{personal.get('phone','')}",
    "location": "{personal.get('location','')}",
    "linkedin_url": "{personal.get('linkedin','')}",
    "github_url": "{personal.get('github','')}",
    "years_of_experience": "0-1 years",
    "current_ctc": "Fresher",
    "expected_ctc": "As per industry",
    "notice_period": "Immediate joiner",
    "skills_summary": "{', '.join(skills[:8])}"
  }}
}}"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1000, temperature=0.1
    )
    text = response.choices[0].message.content
    m = re.search(r'\{.*\}', text, re.DOTALL)
    if m:
        try: return json.loads(m.group())
        except: pass
    return {"company_name": "N/A", "job_title": "N/A", "form_fill_data": {}}
