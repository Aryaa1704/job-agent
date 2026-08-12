import streamlit as st
import json
import os
import sys

sys.path.append('/workspaces/job-agent')

from ai.resume_builder import build_docx_resume, ai_tailor_content, generate_ats_score
from ai.resume_parser import extract_resume_text

def render_resume_tab(profile):
    st.header("📄 ATS Resume Builder")
    st.markdown("Real data se ATS-optimized DOCX resume — photo, links, live editor")
    st.markdown("---")

    st.subheader("1️⃣ Job Description")
    resume_jd = st.text_area("JD paste karo", height=150, key="r_jd",
                               placeholder="Software Engineer at Google...")
    if 'last_jd' in st.session_state:
        if st.button("⚡ Last analyzed JD use karo"):
            st.session_state['r_jd'] = st.session_state['last_jd']
            st.rerun()

    st.markdown("---")
    st.subheader("2️⃣ Apna Resume Do")
    mode = st.radio("", [
        "🚀 Profile.json use karo",
        "📁 File upload karo (PDF/DOCX/TXT)",
        "📋 Text paste karo"
    ], horizontal=True)

    existing_text = ""
    if mode == "📁 File upload karo (PDF/DOCX/TXT)":
        uploaded = st.file_uploader("Resume file", type=["pdf","docx","doc","txt"])
        if uploaded:
            existing_text = extract_resume_text(uploaded)
            st.success(f"✅ {len(existing_text)} characters extracted")
            with st.expander("Extracted text dekho"):
                st.text(existing_text[:1500])
    elif mode == "📋 Text paste karo":
        existing_text = st.text_area("Resume paste karo", height=200, key="paste_r",
            placeholder="Aryan Sharma\naryan@gmail.com\n\nEXPERIENCE\n...")
        if existing_text:
            st.success(f"✅ {len(existing_text)} characters ready")

    st.markdown("---")
    st.subheader("3️⃣ Photo & Links (Optional)")
    col_ph, col_lk = st.columns([1, 2])

    photo_path = ""
    with col_ph:
        photo = st.file_uploader("📷 Profile Photo", type=["png","jpg","jpeg"])
        if photo:
            os.makedirs("output", exist_ok=True)
            photo_path = f"output/photo_{photo.name}"
            with open(photo_path, "wb") as f:
                f.write(photo.read())
            st.image(photo_path, width=120)
            st.success("Photo ready!")

    with col_lk:
        personal = profile.get("personal", profile)
        linkedin_val = st.text_input("LinkedIn URL", value=personal.get("linkedin",""),
            placeholder="https://linkedin.com/in/yourname")
        github_val = st.text_input("GitHub URL", value=personal.get("github",""),
            placeholder="https://github.com/yourname")
        portfolio_val = st.text_input("Portfolio (optional)", placeholder="https://yoursite.com")

        if "personal" in profile:
            profile["personal"]["linkedin"] = linkedin_val
            profile["personal"]["github"] = github_val
        else:
            profile["linkedin"] = linkedin_val
            profile["github"] = github_val

    st.markdown("---")
    st.subheader("4️⃣ Generate Resume")

    if st.button("🚀 Generate ATS Resume", type="primary"):
        jd_text = resume_jd or st.session_state.get('r_jd','')
        if not jd_text.strip():
            st.error("❌ JD paste karo Step 1 mein!")
        else:
            with st.spinner("🤖 AI real content tailor kar raha hai... (30-60 sec)"):
                try:
                    docx_path = build_docx_resume(
                        profile=profile,
                        jd=jd_text,
                        existing_resume=existing_text,
                        photo_path=photo_path
                    )
                    st.session_state['docx_path'] = docx_path
                    st.session_state['resume_jd_used'] = jd_text

                    tailored = ai_tailor_content(jd_text, profile, existing_text)
                    personal_info = profile.get("personal", profile)
                    tailored["name"] = personal_info.get("name","")
                    tailored["email"] = personal_info.get("email","")
                    tailored["phone"] = personal_info.get("phone","")
                    tailored["location"] = personal_info.get("location","")
                    tailored["linkedin"] = linkedin_val
                    tailored["github"] = github_val
                    st.session_state['tailored_data'] = tailored
                    st.success("✅ Resume ready! Neeche download karo.")
                except Exception as e:
                    st.error(f"Error: {e}")

    if 'docx_path' in st.session_state and os.path.exists(st.session_state['docx_path']):
        st.markdown("---")
        st.subheader("5️⃣ Edit & Download")

        td = st.session_state.get('tailored_data', {})
        e1, e2, e3, e4, e5 = st.tabs([
            "👤 Personal", "📝 Summary & Skills",
            "💼 Experience", "🚀 Projects", "🎓 Education"
        ])

        with e1:
            ec1, ec2 = st.columns(2)
            with ec1:
                e_name = st.text_input("Full Name", value=td.get("name",""))
                e_email = st.text_input("Email", value=td.get("email",""))
                e_phone = st.text_input("Phone", value=td.get("phone",""))
            with ec2:
                e_location = st.text_input("Location", value=td.get("location",""))
                e_linkedin = st.text_input("LinkedIn", value=td.get("linkedin", linkedin_val))
                e_github = st.text_input("GitHub", value=td.get("github", github_val))

        with e2:
            e_summary = st.text_area("Summary", value=td.get("summary",""), height=120)
            st.markdown("**Skills:**")
            skills_data = td.get("skills", {})
            edited_skills = {}
            for cat, items in skills_data.items():
                val = st.text_input(cat, value=", ".join(items) if isinstance(items, list) else str(items))
                edited_skills[cat] = [x.strip() for x in val.split(",") if x.strip()]

        with e3:
            edited_exp = []
            for i, exp in enumerate(td.get("experience",[])):
                with st.expander(f"💼 {exp.get('title','')} @ {exp.get('company','')}"):
                    et = st.text_input("Title", value=exp.get("title",""), key=f"et_{i}")
                    ec = st.text_input("Company", value=exp.get("company",""), key=f"ec_{i}")
                    ed = st.text_input("Duration", value=exp.get("duration",""), key=f"ed_{i}")
                    pts = exp.get("points", exp.get("bullets",[]))
                    ep = st.text_area("Bullets (1 line = 1 bullet)", value="\n".join(pts), height=150, key=f"ep_{i}")
                    edited_exp.append({"title":et,"company":ec,"duration":ed,
                        "points":[x.strip() for x in ep.split("\n") if x.strip()]})

        with e4:
            edited_proj = []
            for i, proj in enumerate(td.get("projects",[])):
                with st.expander(f"🚀 {proj.get('name','')}"):
                    pn = st.text_input("Name", value=proj.get("name",""), key=f"pn_{i}")
                    pt = st.text_input("Tech", value=proj.get("tech",""), key=f"pt_{i}")
                    pp = st.text_area("Bullets", value="\n".join(proj.get("points",proj.get("bullets",[]))), height=120, key=f"pp_{i}")
                    pg = st.text_input("GitHub", value=proj.get("github",proj.get("link","")), key=f"pg_{i}")
                    edited_proj.append({"name":pn,"tech":pt,"github":pg,
                        "points":[x.strip() for x in pp.split("\n") if x.strip()]})

        with e5:
            edited_edu = []
            for i, edu in enumerate(td.get("education",[])):
                with st.expander(f"🎓 {edu.get('degree','')}"):
                    edeg = st.text_input("Degree", value=edu.get("degree",""), key=f"edeg_{i}")
                    einst = st.text_input("Institution", value=edu.get("institution",edu.get("college","")), key=f"einst_{i}")
                    eyr = st.text_input("Year", value=edu.get("year",""), key=f"eyr_{i}")
                    ecgpa = st.text_input("CGPA", value=edu.get("cgpa",""), key=f"ecgpa_{i}")
                    edited_edu.append({"degree":edeg,"institution":einst,"year":eyr,"cgpa":ecgpa})

        st.markdown("---")
        if st.button("🔄 Rebuild with My Changes", type="primary"):
            overrides = {
                "name":e_name, "email":e_email, "phone":e_phone,
                "location":e_location, "linkedin":e_linkedin, "github":e_github,
                "summary":e_summary, "skills":edited_skills,
                "experience":edited_exp, "projects":edited_proj, "education":edited_edu
            }
            with st.spinner("Rebuilding..."):
                try:
                    new_path = build_docx_resume(
                        profile=profile,
                        jd=st.session_state.get('resume_jd_used',''),
                        photo_path=photo_path,
                        manual_overrides=overrides
                    )
                    st.session_state['docx_path'] = new_path
                    st.success("✅ Resume updated!")
                except Exception as e:
                    st.error(f"Error: {e}")

        st.markdown("---")
        st.subheader("⬇️ Download")
        d1, d2 = st.columns(2)
        with d1:
            with open(st.session_state['docx_path'], "rb") as f:
                st.download_button("⬇️ Download DOCX", data=f.read(),
                    file_name="my_ats_resume.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    type="primary")
        with d2:
            if st.button("🎯 ATS Score Check"):
                resume_text = json.dumps(st.session_state.get('tailored_data',{}))
                jd_used = st.session_state.get('resume_jd_used','')
                with st.spinner("Analyzing..."):
                    ats = generate_ats_score(resume_text, jd_used)
                sc = ats.get('ats_score',0)
                if sc>=80: st.success(f"✅ ATS Score: {sc}%")
                elif sc>=60: st.warning(f"⚠️ ATS Score: {sc}%")
                else: st.error(f"❌ ATS Score: {sc}%")
                st.progress(sc/100)
                r1,r2 = st.columns(2)
                with r1:
                    for k in ats.get('matched_keywords',[]): st.write(f"🟢 {k}")
                with r2:
                    for k in ats.get('missing_keywords',[]): st.write(f"🔴 {k}")
                for imp in ats.get('improvements',[]): st.write(f"📝 {imp}")
