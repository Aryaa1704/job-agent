import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime

def scrape_remoteok(keywords=["python", "django", "backend"]):
    """RemoteOK se jobs scrape karo — no login needed"""
    jobs = []
    try:
        url = "https://remoteok.com/api"
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(url, headers=headers, timeout=10)
        data = res.json()
        
        for job in data[1:]:  # first item is metadata
            title = job.get("position", "").lower()
            desc = job.get("description", "").lower()
            
            # keyword match check
            if any(k in title or k in desc for k in keywords):
                jobs.append({
                    "title": job.get("position", "N/A"),
                    "company": job.get("company", "N/A"),
                    "location": "Remote",
                    "url": job.get("url", ""),
                    "description": job.get("description", "")[:500],
                    "date": job.get("date", ""),
                    "source": "RemoteOK"
                })
    except Exception as e:
        print(f"RemoteOK error: {e}")
    
    return jobs

def scrape_himalayas(keyword="python"):
    """Himalayas.app se jobs"""
    jobs = []
    try:
        url = f"https://himalayas.app/jobs/api?q={keyword}"
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(url, headers=headers, timeout=10)
        data = res.json()
        
        for job in data.get("jobs", [])[:10]:
            jobs.append({
                "title": job.get("title", "N/A"),
                "company": job.get("companyName", "N/A"),
                "location": job.get("location", "Remote"),
                "url": job.get("url", ""),
                "description": job.get("description", "")[:500],
                "date": job.get("publishedAt", ""),
                "source": "Himalayas"
            })
    except Exception as e:
        print(f"Himalayas error: {e}")
    
    return jobs

def get_all_jobs(keywords=["python", "django"]):
    """Saari sources se jobs lao"""
    all_jobs = []
    
    print("🔍 RemoteOK scraping...")
    all_jobs.extend(scrape_remoteok(keywords))
    
    for kw in keywords[:2]:
        print(f"🔍 Himalayas scraping: {kw}")
        all_jobs.extend(scrape_himalayas(kw))
    
    # Save to file
    output = {
        "scraped_at": datetime.now().isoformat(),
        "total": len(all_jobs),
        "jobs": all_jobs
    }
    
    with open("data/scraped_jobs.json", "w") as f:
        json.dump(output, f, indent=2)
    
    print(f"✅ {len(all_jobs)} jobs mili! data/scraped_jobs.json mein save hui")
    return all_jobs

if __name__ == "__main__":
    jobs = get_all_jobs(["python", "django", "backend"])
    for j in jobs[:3]:
        print(f"\n📌 {j['title']} @ {j['company']} ({j['source']})")
