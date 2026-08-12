import os
import json
import re
import subprocess
import tempfile
from groq import Groq

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def ai_tailor_content(jd: str, raw_profile: dict, existing_resume: str = "") -> dict:
    """
    AI real content tailor karta hai — fake nahi, profile/resume se hi lega
    """
    prompt = f"""
You are an ATS resume expert. Tailor the candidate's REAL data for this job.

CANDIDATE DATA:
{json.dumps(raw_profile, indent=2)}

{"EXISTING RESUME TEXT:\n" + existing_resume if existing_resume.strip() else ""}

TARGET JOB DESCRIPTION:
{jd}

RULES:
- Use ONLY real information from candidate data — NEVER invent fake companies, degrees, or projects
- Rewrite bullets using JD keywords naturally
- Use STAR format: Action verb + what + result/metric
- Strong verbs: Developed, Built, Engineered, Optimized, Designed, Led, Reduced, Increased
- Summary should mention the exact role from JD
- Skills: only real skills candidate has, reordered to match JD priority

Return ONLY valid JSON (no markdown, no explanation):
{{
  "summary": "2-3 sentence professional summary tailored to this JD",
  "skills": {{
    "Languages": ["Python", "..."],
    "Frameworks": ["Django", "..."],
    "Databases": ["PostgreSQL", "..."],
    "Tools & Platforms": ["Git", "AWS", "..."],
    "Concepts": ["REST APIs", "..."]
  }},
  "experience": [
    {{
      "title": "exact title from profile",
      "company": "exact company from profile",
      "duration": "exact dates from profile",
      "points": [
        "Developed X using Y, resulting in Z% improvement",
        "Built REST APIs with Django serving 10k+ requests/day",
        "Optimized PostgreSQL queries reducing response time by 40%"
      ]
    }}
  ],
  "projects": [
    {{
      "name": "exact project name",
      "tech": "tech stack used",
      "points": [
        "Built X that does Y, achieving Z",
        "Implemented feature using technology"
      ],
      "github": "github url if available"
    }}
  ],
  "education": [
    {{
      "degree": "exact degree",
      "institution": "exact college",
      "year": "year",
      "cgpa": "cgpa if available"
    }}
  ],
  "certifications": ["cert name — issuer"]
}}
"""
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=3000,
        temperature=0.2
    )
    text = response.choices[0].message.content
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except:
            pass
    return {}


def build_docx_resume(profile: dict, jd: str,
                       existing_resume: str = "",
                       photo_path: str = "",
                       manual_overrides: dict = None) -> str:
    """
    Full pipeline: AI tailor → DOCX generate → return path
    """
    # Personal info
    personal = profile.get("personal", profile)

    # AI se tailored content lo
    tailored = ai_tailor_content(jd, profile, existing_resume)

    if manual_overrides:
        tailored.update(manual_overrides)

    # Final data assemble karo
    resume_data = {
        "name": personal.get("name", ""),
        "email": personal.get("email", ""),
        "phone": personal.get("phone", ""),
        "location": personal.get("location", ""),
        "linkedin": personal.get("linkedin", ""),
        "github": personal.get("github", ""),
        "photo_path": photo_path or "",
        **tailored
    }

    # Temp files
    data_file = tempfile.mktemp(suffix=".json")
    output_file = "output/resume.docx"
    os.makedirs("output", exist_ok=True)

    with open(data_file, "w") as f:
        json.dump(resume_data, f, indent=2)

    # Node script run karo
    script = os.path.join(os.path.dirname(__file__), "docx_resume_generator.js")
    result = subprocess.run(
        ["node", script, data_file, output_file],
        capture_output=True, text=True
    )

    os.unlink(data_file)

    if "SUCCESS" in result.stdout:
        return output_file
    else:
        raise Exception(f"DOCX generation failed: {result.stderr}")


def generate_ats_score(resume_text: str, jd: str) -> dict:
    prompt = f"""
Analyze this resume against the job description for ATS compatibility.
RESUME: {resume_text[:2500]}
JOB DESCRIPTION: {jd[:1200]}

Return ONLY valid JSON:
{{
  "ats_score": <0-100>,
  "keyword_match_percent": <0-100>,
  "matched_keywords": ["kw1", "kw2"],
  "missing_keywords": ["kw1", "kw2"],
  "format_issues": ["issue1"],
  "improvements": ["suggestion1"],
  "strengths": ["strength1"]
}}
"""
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=600, temperature=0.1
    )
    text = response.choices[0].message.content
    m = re.search(r'\{.*\}', text, re.DOTALL)
    if m:
        try: return json.loads(m.group())
        except: pass
    return {"ats_score": 0, "error": "parse failed"}
