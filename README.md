# Job Agent 🤖

Personal AI-powered job application agent built for automated job discovery, 
resume tailoring, and application submission.

## What It Does

- Fetches jobs from Naukri, Indeed, Internshala, Unstop, 
  Wellfound, Cutshort, and company career pages
- AI analyzes each JD and gives match score (0-100)
- Automatically tailors resume per job description
- Applies to jobs via browser automation
- Asks you only when human input is needed (CAPTCHA, unknown questions)
- Remembers your answers — never asks same question twice

## Tech Stack

- **Language** — Python
- **AI** — Claude API (Anthropic)
- **Automation** — Playwright
- **Dashboard** — Streamlit
- **Database** — SQLite
- **Resume** — python-docx + reportlab

## Project Structure

\`\`\`
job-agent/
├── config.py              # API keys, settings
├── data/
│   ├── profile.json       # Your master profile
│   ├── question_memory.json
│   └── resumes/           # Generated resumes
├── core/                  # Database, models
├── ai/                    # Match scorer, resume tailor
├── fetchers/              # Job discovery per platform
├── agent/                 # Browser automation + adapters
└── dashboard/             # Streamlit UI
\`\`\`

## Supported Platforms

| Platform | Fetch | Apply |
|---|---|---|
| Greenhouse (career pages) | ✅ | ✅ |
| Lever (career pages) | ✅ | ✅ |
| Indeed India | ✅ | ✅ |
| Internshala | ✅ | ✅ |
| Unstop | ✅ | ✅ |
| AngelList/Wellfound | ✅ | ✅ |
| Cutshort | ✅ | ✅ |
| Naukri | ✅ | 🔄 |
| Workday | 🔄 | 🔄 |

✅ Ready &nbsp;&nbsp; 🔄 In Progress

## Setup

\`\`\`bash
# Install dependencies
pip install anthropic python-docx reportlab streamlit 
playwright requests beautifulsoup4

# Install browser
playwright install chromium

# Add API key
export ANTHROPIC_API_KEY="your-key-here"

# Initialize database
python -c "from core.database import init_db; init_db()"

# Run dashboard
streamlit run dashboard/app.py
\`\`\`

## How It Works

\`\`\`
Your Profile + Master Resume
         ↓
   Job Discovery
   (all platforms)
         ↓
   AI Match Score
   (0-100 per job)
         ↓
   Resume Tailoring
   (per JD, no facts invented)
         ↓
   Auto Apply
   (human confirmation if needed)
         ↓
   Application Tracker
\`\`\`

## Status

🚧 Active Development

---
Built for personal use.
