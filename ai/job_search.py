import urllib.parse

def generate_search_links(job_title: str, location: str = "India", skills: list = [], experience: str = "fresher") -> dict:
    t = urllib.parse.quote(job_title)
    l = urllib.parse.quote(location)
    jt = job_title.lower().replace(' ', '-')
    loc = location.lower().replace(' ', '-')

    return {
        "🇮🇳 Naukri": {
            "url": f"https://www.naukri.com/{jt}-jobs?k={t}&l={l}",
            "description": "India #1 job portal", "type": "indian", "quick_apply": True
        },
        "🇮🇳 Internshala": {
            "url": f"https://internshala.com/internships/{jt}-internship",
            "description": "Best for freshers", "type": "indian", "quick_apply": True
        },
        "🇮🇳 Foundit (Monster)": {
            "url": f"https://www.foundit.in/srp/results?query={t}&location={l}",
            "description": "Monster India", "type": "indian", "quick_apply": False
        },
        "🇮🇳 Shine": {
            "url": f"https://www.shine.com/job-search/{jt}-jobs-in-{loc}",
            "description": "Shine.com", "type": "indian", "quick_apply": False
        },
        "🇮🇳 Apna": {
            "url": f"https://apna.co/jobs/{jt}",
            "description": "Entry-level jobs", "type": "indian", "quick_apply": True
        },
        "🇮🇳 Freshersworld": {
            "url": f"https://www.freshersworld.com/jobs/jobsearch/{jt}-jobs-in-{loc}",
            "description": "Freshers specific", "type": "indian", "quick_apply": True
        },
        "🇮🇳 Instahyre": {
            "url": f"https://instahyre.com/candidate/opportunities/?q={t}",
            "description": "Direct recruiter connect", "type": "indian", "quick_apply": True
        },
        "🌐 LinkedIn": {
            "url": f"https://www.linkedin.com/jobs/search/?keywords={t}&location={l}",
            "description": "Professional network", "type": "global", "quick_apply": True
        },
        "🌐 Indeed India": {
            "url": f"https://in.indeed.com/jobs?q={t}&l={l}",
            "description": "Massive job database", "type": "global", "quick_apply": False
        },
        "🌐 Wellfound": {
            "url": f"https://wellfound.com/jobs?q={t}&l={l}",
            "description": "Startup jobs", "type": "global", "quick_apply": True
        },
        "🌐 Glassdoor": {
            "url": f"https://www.glassdoor.co.in/Job/india-{jt}-jobs-SRCH_IL.0,5_IN115_KO6,{6+len(job_title)}.htm",
            "description": "Jobs + reviews", "type": "global", "quick_apply": False
        },
        "💻 RemoteOK": {
            "url": f"https://remoteok.com/remote-{jt}-jobs",
            "description": "Remote-only jobs", "type": "remote", "quick_apply": True
        },
        "💻 Turing": {
            "url": f"https://www.turing.com/jobs/{jt}",
            "description": "Remote with US companies", "type": "remote", "quick_apply": False
        },
        "💻 HackerNews Jobs": {
            "url": "https://news.ycombinator.com/jobs",
            "description": "YC startup jobs", "type": "remote", "quick_apply": False
        },
        "🏢 Google Careers": {
            "url": f"https://careers.google.com/jobs/results/?q={t}&location={l}",
            "description": "Direct Google apply", "type": "career_page", "quick_apply": False
        },
        "🏢 Microsoft": {
            "url": f"https://jobs.microsoft.com/en-us/search?q={t}",
            "description": "Direct Microsoft apply", "type": "career_page", "quick_apply": False
        },
        "🏢 Amazon": {
            "url": f"https://www.amazon.jobs/en/search?base_query={t}&loc_query={l}",
            "description": "Direct Amazon apply", "type": "career_page", "quick_apply": False
        },
        "🏢 TCS": {
            "url": "https://www.tcs.com/careers/tcs-careers",
            "description": "Direct TCS apply", "type": "career_page", "quick_apply": False
        },
        "🏢 Infosys": {
            "url": f"https://career.infosys.com/joblist#SearchByJobRole={job_title}",
            "description": "Direct Infosys apply", "type": "career_page", "quick_apply": False
        },
        "🏢 Wipro": {
            "url": f"https://careers.wipro.com/careers-home/jobs?keyword={t}",
            "description": "Direct Wipro apply", "type": "career_page", "quick_apply": False
        },
        "🏢 Razorpay": {
            "url": f"https://razorpay.com/jobs/",
            "description": "Razorpay careers", "type": "career_page", "quick_apply": False
        },
        "🏢 Zerodha": {
            "url": "https://zerodha.com/careers/",
            "description": "Zerodha careers", "type": "career_page", "quick_apply": False
        },
    }


def get_email_template(package: dict, cover_letter: str, profile: dict) -> str:
    personal = profile.get("personal", profile)
    return f"""Subject: Application for {package.get('job_title', 'Position')} — {personal.get('name', '')}

Dear Hiring Manager,

{cover_letter[:500]}

Please find my resume attached.

Best regards,
{personal.get('name', '')}
{personal.get('email', '')} | {personal.get('phone', '')}
LinkedIn: {personal.get('linkedin', '')}
GitHub: {personal.get('github', '')}"""
