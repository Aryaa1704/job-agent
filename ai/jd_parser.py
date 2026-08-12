from groq import Groq
import json, os

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def parse_jd(job_description: str) -> dict:
    prompt = f"""
Extract structured info from this job description.
Return ONLY JSON, no markdown, no explanation.

JOB DESCRIPTION:
{job_description}

Return exactly:
{{
  "title": "",
  "company": "",
  "location": "",
  "salary": "",
  "job_type": "full-time/internship/contract",
  "experience_required": "",
  "required_skills": [],
  "preferred_skills": [],
  "responsibilities": [],
  "qualifications": []
}}
"""
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1024
    )
    text = response.choices[0].message.content.strip()
    if "```" in text:
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
    return json.loads(text.strip())
