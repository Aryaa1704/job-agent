import json
from datetime import datetime

TRACKER_FILE = "data/applied_jobs.json"

def load_tracker():
    try:
        with open(TRACKER_FILE, "r") as f:
            return json.load(f)
    except:
        return []

def save_tracker(data):
    with open(TRACKER_FILE, "w") as f:
        json.dump(data, f, indent=2)

def mark_applied(job_title, company, url="", notes=""):
    tracker = load_tracker()
    entry = {
        "id": len(tracker) + 1,
        "title": job_title,
        "company": company,
        "url": url,
        "notes": notes,
        "status": "applied",
        "applied_date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "follow_up_date": None,
        "interview_date": None,
        "result": "pending"
    }
    tracker.append(entry)
    save_tracker(tracker)
    print(f"✅ Saved: {job_title} @ {company}")
    return entry

def update_status(job_id, status, notes=""):
    """Status update: applied/interview/rejected/offered/accepted"""
    tracker = load_tracker()
    for job in tracker:
        if job["id"] == job_id:
            job["status"] = status
            job["result"] = status
            if notes:
                job["notes"] = notes
            print(f"✅ Updated job #{job_id} → {status}")
            break
    save_tracker(tracker)

def show_all():
    tracker = load_tracker()
    print(f"\n📊 Applied Jobs ({len(tracker)} total):\n")
    for job in tracker:
        emoji = {"applied": "📤", "interview": "🎯", "rejected": "❌", 
                 "offered": "🎉", "accepted": "✅", "pending": "⏳"}.get(job["status"], "📋")
        print(f"{emoji} [{job['id']}] {job['title']} @ {job['company']} | {job['status']} | {job['applied_date']}")

if __name__ == "__main__":
    show_all()
