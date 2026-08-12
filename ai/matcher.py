from groq import Groq
import json, os

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def analyze_job(job_description: str, profile: dict) -> dict:
    prompt = f"""
You are an expert job matcher.

CANDIDATE PROFILE:
{json.dumps(profile, indent=2)}

JOB DESCRIPTION:
{job_description}

Return ONLY a JSON object, no markdown, no explanation:
{{
  "match_score": <0-100>,
  "matched_skills": [],
  "missing_skills": [],
  "missing_info_needed": [],
  "recommendation": "apply/skip/maybe",
  "reason": "one line explanation"
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
