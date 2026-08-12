import os
import json
import re
from groq import Groq

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def tailor_resume(jd: str, profile: dict, existing_resume: str = "") -> str:
    """
    ATS resume banao — profile.json se ya existing resume se
    """
    skills = profile.get("skills", [])
    if isinstance(skills, dict):
        all_skills = []
        for v in skills.values():
            if isinstance(v, list):
                all_skills.extend(v)
        skills = all_skills

    personal = profile.get("personal", profile)
    experience = profile.get("experience", [])
    education = profile.get("education", [])
    projects = profile.get("projects", [])

    if existing_resume.strip():
        # Existing resume se tailor karo
        source_section = f"""
CANDIDATE'S EXISTING RESUME (use this as the primary source):
{existing_resume}

Also use this profile data to fill any gaps:
Name: {personal.get('name', 'N/A')}
Email: {personal.get('email', 'N/A')}
Phone: {personal.get('phone', 'N/A')}
"""
    else:
        # profile.json se banao
        source_section = f"""
CANDIDATE PROFILE:
Name: {personal.get('name', 'N/A')}
Email: {personal.get('email', 'N/A')}
Phone: {personal.get('phone', 'N/A')}
Location: {personal.get('location', 'N/A')}
LinkedIn: {personal.get('linkedin', 'N/A')}
GitHub: {personal.get('github', 'N/A')}
Skills: {', '.join(skills)}
Experience: {json.dumps(experience, indent=2)}
Education: {json.dumps(education, indent=2)}
Projects: {json.dumps(projects, indent=2)}
"""

    prompt = f"""
You are an expert ATS resume writer. Create a professional ATS-optimized resume.

{source_section}

TARGET JOB DESCRIPTION:
{jd}

STRICT RULES:
1. Extract ALL important keywords from JD — include them naturally
2. Use STAR format bullets: Action Verb + Task + Result + Metric
3. Strong action verbs: Developed, Built, Optimized, Engineered, Led, Designed, Reduced, Increased
4. Add REAL metrics where possible (%, numbers, scale)
5. ATS-safe format: NO tables, NO columns, NO special characters
6. Keep ALL real experience from the candidate — don't remove anything
7. Reframe existing bullets to match JD keywords
8. Section order: Contact → Summary → Skills → Experience → Projects → Education

OUTPUT — plain text only, use these exact section headers in CAPS:

[FULL NAME]
[email] | [phone] | [location]
LinkedIn: [url] | GitHub: [url]

PROFESSIONAL SUMMARY
[3 lines: role from JD + top skills + years exp + impact]

TECHNICAL SKILLS
Languages: [list]
Frameworks & Libraries: [list]  
Databases: [list]
Tools & Platforms: [list]
Concepts: [list]

PROFESSIONAL EXPERIENCE
[Job Title] | [Company Name] | [Start – End]
- [Strong bullet with metric]
- [Strong bullet with metric]
- [Strong bullet with metric]

PROJECTS
[Project Name] | [Tech Stack used]
- [What it does + scale/impact]
- [Key achievement]
GitHub: [link if available]

EDUCATION
[Degree] | [Institution] | [Year]
CGPA: [if available] | Relevant: [key courses]

CERTIFICATIONS
- [cert name] — [issuer] [year if known]

Write everything in plain text. Be specific, impactful, and keyword-rich.
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=2500,
        temperature=0.3
    )
    return response.choices[0].message.content


def generate_ats_score(resume_text: str, jd: str) -> dict:
    prompt = f"""
Analyze this resume against the job description for ATS compatibility.

RESUME:
{resume_text[:3000]}

JOB DESCRIPTION:
{jd[:1500]}

Return ONLY valid JSON:
{{
  "ats_score": <0-100>,
  "keyword_match_percent": <0-100>,
  "matched_keywords": ["kw1", "kw2"],
  "missing_keywords": ["kw1", "kw2"],
  "format_issues": ["issue1"],
  "improvements": ["suggestion1", "suggestion2"],
  "strengths": ["strength1", "strength2"]
}}
"""
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=800,
        temperature=0.1
    )
    text = response.choices[0].message.content
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except:
            pass
    return {"ats_score": 0, "error": "Parse failed"}
