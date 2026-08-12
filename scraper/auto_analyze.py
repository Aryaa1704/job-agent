import json
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai.matcher import analyze_job
from scraper.job_scraper import get_all_jobs

def run_auto_analysis():
    """Scrape karo + analyze karo + results save karo"""
    
    # Profile load karo
    with open("data/profile.json", "r") as f:
        profile = json.load(f)
    
    print("🚀 Jobs scraping shuru...")
    jobs = get_all_jobs(["python", "django", "backend", "fastapi"])
    
    results = []
    apply_list = []
    
    print(f"\n🤖 {len(jobs)} jobs analyze ho rahi hain...\n")
    
    for i, job in enumerate(jobs[:20]):  # top 20 analyze
        try:
            jd_text = f"{job['title']} at {job['company']}\n{job['description']}"
            result = analyze_job(jd_text, profile)
            
            job_result = {
                **job,
                "match_score": result["match_score"],
                "recommendation": result["recommendation"],
                "matched_skills": result.get("matched_skills", []),
                "missing_skills": result.get("missing_skills", []),
                "reason": result.get("reason", "")
            }
            
            results.append(job_result)
            
            if result["recommendation"] == "apply":
                apply_list.append(job_result)
                print(f"✅ APPLY: {job['title']} @ {job['company']} — {result['match_score']}%")
            elif result["recommendation"] == "maybe":
                print(f"🟡 MAYBE: {job['title']} @ {job['company']} — {result['match_score']}%")
            else:
                print(f"❌ SKIP:  {job['title']} @ {job['company']} — {result['match_score']}%")
                
        except Exception as e:
            print(f"⚠️ Error: {job['title']} — {e}")
    
    # Save results
    with open("data/analysis_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    with open("data/apply_list.json", "w") as f:
        json.dump(apply_list, f, indent=2)
    
    print(f"\n🎯 SUMMARY:")
    print(f"   Total analyzed: {len(results)}")
    print(f"   Apply karo:     {len(apply_list)}")
    print(f"   Results saved:  data/analysis_results.json")
    print(f"   Apply list:     data/apply_list.json")
    
    return results, apply_list

if __name__ == "__main__":
    run_auto_analysis()
