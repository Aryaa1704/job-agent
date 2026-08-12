import streamlit as st
import json, sys, os

sys.path.append('/workspaces/job-agent')

from ai.matcher import analyze_job
from ai.jd_parser import parse_jd
from dashboard.resume_tab import render_resume_tab
from dashboard.apply_tab import render_apply_tab

st.set_page_config(page_title="AI Job Agent", page_icon="🤖", layout="wide")
st.title("🤖 AI Job Agent Dashboard")
st.markdown("---")

with open("data/profile.json","r") as f:
    profile = json.load(f)

skills = profile.get('skills',[])
if isinstance(skills, dict):
    all_skills = []
    for v in skills.values():
        if isinstance(v, list): all_skills.extend(v)
    skills = all_skills

personal = profile.get('personal',{})
st.sidebar.header("👤 Your Profile")
st.sidebar.write(f"**Name:** {personal.get('name', profile.get('name','N/A'))}")
st.sidebar.write(f"**Skills:** {', '.join(skills[:5])}")

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🔍 Job Analyzer",
    "📄 ATS Resume Builder",
    "📋 Auto Results",
    "📊 Tracker",
    "🚀 Smart Apply"
])

with tab1:
    st.header("🔍 Job Match Analyzer")
    jd = st.text_area("Paste Job Description", height=200, placeholder="JD yahan paste karo...")
    if st.button("🔍 Analyze Job", type="primary"):
        if jd.strip():
            with st.spinner("Analyzing..."):
                parsed = parse_jd(jd)
                result = analyze_job(jd, profile)
            st.session_state['last_jd'] = jd
            st.markdown("---")
            c1,c2 = st.columns(2)
            with c1:
                st.subheader("📊 Job Details")
                for k,v in [("Title","title"),("Company","company"),("Location","location"),("Salary","salary"),("Experience","experience_required")]:
                    st.write(f"**{k}:** {parsed.get(v,'N/A')}")
            with c2:
                st.subheader("🎯 Match")
                sc = result['match_score']
                if sc>=85: st.success(f"✅ {sc}%")
                elif sc>=70: st.warning(f"⚠️ {sc}%")
                else: st.error(f"❌ {sc}%")
                st.progress(sc/100)
                rec = result['recommendation']
                if rec=="apply": st.success("🟢 APPLY")
                elif rec=="maybe": st.warning("🟡 MAYBE")
                else: st.error("🔴 SKIP")
                st.write(f"**Reason:** {result['reason']}")
            c3,c4 = st.columns(2)
            with c3:
                st.subheader("✅ Matched")
                for s in result.get('matched_skills',[]): st.write(f"🟢 {s}")
            with c4:
                st.subheader("❌ Missing")
                for s in result.get('missing_skills',[]): st.write(f"🔴 {s}")
            st.info("📄 ATS Resume ke liye next tab!")
        else:
            st.error("JD paste karo!")

with tab2:
    render_resume_tab(profile)

with tab3:
    st.header("📋 Auto-Analyzed Jobs")
    if st.button("🚀 Run Scraper"):
        with st.spinner("Scraping..."):
            try:
                from scraper.auto_analyze import run_auto_analysis
                r, a = run_auto_analysis()
                st.success(f"{len(r)} analyzed, {len(a)} apply karo")
            except Exception as e:
                st.error(f"Error: {e}")
    try:
        with open("data/analysis_results.json") as f:
            results = json.load(f)
        filt = st.selectbox("Filter:",["All","apply","maybe","skip"])
        for job in results:
            if filt!="All" and job.get("recommendation")!=filt: continue
            sc = job.get("match_score",0)
            rec = job.get("recommendation","skip")
            icon = "🟢" if rec=="apply" else "🟡" if rec=="maybe" else "🔴"
            with st.expander(f"{icon} {job['title']} @ {job['company']} — {sc}%"):
                st.write(f"**Reason:** {job.get('reason','N/A')}")
                if job.get('url'): st.markdown(f"[🔗 Apply]({job['url']})")
    except:
        st.info("Auto scraper chalao pehle!")

with tab4:
    st.header("📊 Application Tracker")
    with st.expander("➕ Add Application"):
        t1=st.text_input("Job Title"); t2=st.text_input("Company")
        t3=st.text_input("URL"); t4=st.text_area("Notes",height=60)
        if st.button("💾 Save"):
            if t1 and t2:
                from tracker.tracker import mark_applied
                mark_applied(t1,t2,t3,t4)
                st.success("Saved!"); st.rerun()
            else: st.error("Title + Company chahiye!")
    try:
        with open("data/applied_jobs.json") as f:
            applied = json.load(f)
        em={"applied":"📤","interview":"🎯","rejected":"❌","offered":"🎉","accepted":"✅","pending":"⏳"}
        for job in reversed(applied):
            with st.expander(f"{em.get(job['status'],'📋')} {job['title']} @ {job['company']} | {job['applied_date']}"):
                ns=st.selectbox("Status:",["applied","interview","rejected","offered","accepted"],key=f"s_{job['id']}")
                if st.button("Update",key=f"u_{job['id']}"):
                    from tracker.tracker import update_status
                    update_status(job["id"],ns)
                    st.success("Updated!"); st.rerun()
    except:
        st.info("Koi application nahi abhi.")

with tab5:
    render_apply_tab(profile)
