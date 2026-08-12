import os

# Gemini API Key environment se fetch kar rahe hain
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# Baki saari purani settings same rahengi
DB_PATH = "data/jobs.db"
RESUME_OUTPUT = "data/resumes/"
AUTO_APPLY_THRESHOLD = 85
MIN_SHOW_THRESHOLD = 60
DEFAULT_LOCATION = "all india"