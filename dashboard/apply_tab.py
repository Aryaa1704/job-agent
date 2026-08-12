import streamlit as st
import json
import os
import sys
import uuid

sys.path.append('/workspaces/job-agent')

from ai.cover_letter import generate_cover_letter, generate_apply_package
from ai.job_search import generate_search_links, get_email_template

def render_apply_tab(profile):
    st.header("🚀 Smart Apply Assistant")
    st.markdown("JD paste karo → Cover letter + Form data + Direct apply links — sab ek jagah")
    st.markdown("---")

    st.subheader("1️⃣ Job Description")
    col_jd1, col_jd2 = st.columns([3, 1])
    with col_jd1:
        apply_jd = st.text_area("JD paste karo", height=180,
            key="apply_jd_input",
            placeholder="Backend Engineer at Razorpay — Python, Django, 2+ years...")
    with col_jd2:
        if 'last_jd' in st.session_state:
            if st.button("⚡ Last JD load", key="load_last_jd_apply"):
                st.session_state['apply_jd_prefill'] = st.session_state['last_jd']
                st.rerun()
        job_title_manual = st.text_input("Ya job title type karo",
            key="apply_job_title_manual",
            placeholder="Python Developer")
        location_manual = st.text_input("Location",
            key="apply_location_manual",
            value=profile.get('personal', profile).get('location', 'India'))

    tone = st.selectbox("Cover Letter Tone",
        ["professional", "enthusiastic", "concise"],
        key="apply_tone_select")

    analyze_btn = st.button("🔍 Generate Apply Package",
        type="primary", key="apply_generate_btn")

    if analyze_btn:
        jd_text = st.session_state.get('apply_jd_input', '') or st.session_state.get('apply_jd_prefill', '')
        if not jd_text.strip() and not job_title_manual.strip():
            st.error("JD ya Job Title dalo!")
        else:
            with st.spinner("🤖 Package generate ho raha hai..."):
                package = generate_apply_package(jd_text or job_title_manual, profile)
                cover   = generate_cover_letter(jd_text or job_title_manual, profile, tone)

                job_title = package.get('job_title', job_title_manual or 'Software Developer')
                location  = package.get('location', location_manual or 'India')

                skills = profile.get('skills', [])
                if isinstance(skills, dict):
                    all_skills = []
                    for v in skills.values():
                        if isinstance(v, list): all_skills.extend(v)
                    skills = all_skills

                links          = generate_search_links(job_title, location, skills)
                email_template = get_email_template(package, cover, profile)

                st.session_state['apply_package']      = package
                st.session_state['cover_letter']       = cover
                st.session_state['apply_links']        = links
                st.session_state['email_template']     = email_template
                st.session_state['apply_jd_used']      = jd_text
                st.session_state['apply_skills']       = skills

            st.success("✅ Apply package ready!")

    # ── Results ──────────────────────────────────────────────────────────────
    if 'apply_package' not in st.session_state:
        return

    pkg    = st.session_state['apply_package']
    skills = st.session_state.get('apply_skills', [])

    st.markdown("---")
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.metric("🏢 Company",  pkg.get('company_name', 'N/A'))
    with c2: st.metric("💼 Role",     pkg.get('job_title',    'N/A'))
    with c3: st.metric("📍 Location", pkg.get('location',     'N/A'))
    with c4: st.metric("💰 Salary",   pkg.get('salary',       'N/A'))

    st.markdown("---")

    t1, t2, t3, t4, t5 = st.tabs([
        "📋 Form Fill Data",
        "✉️ Cover Letter",
        "🔗 Apply Links",
        "📧 Cold Email",
        "📊 Requirements"
    ])

    # ── TAB: Form Fill ────────────────────────────────────────────────────────
    with t1:
        st.subheader("📋 Form Fill Data — Copy karke form mein paste karo")
        form_data = pkg.get('form_fill_data', {})
        personal  = profile.get('personal', profile)

        fields = [
            ("full_name",       "👤 Full Name",      form_data.get('full_name',          personal.get('name',     ''))),
            ("email",           "📧 Email",           form_data.get('email',              personal.get('email',    ''))),
            ("phone",           "📱 Phone",           form_data.get('phone',              personal.get('phone',    ''))),
            ("location",        "📍 Location",        form_data.get('location',           personal.get('location', ''))),
            ("linkedin",        "🔗 LinkedIn",        form_data.get('linkedin_url',       personal.get('linkedin', ''))),
            ("github",          "🐱 GitHub",          form_data.get('github_url',         personal.get('github',   ''))),
            ("experience",      "⏳ Experience",      form_data.get('years_of_experience','0-1 years')),
            ("current_ctc",     "💰 Current CTC",     form_data.get('current_ctc',        'Fresher')),
            ("expected_ctc",    "💸 Expected CTC",    form_data.get('expected_ctc',       'As per industry')),
            ("notice_period",   "📅 Notice Period",   form_data.get('notice_period',      'Immediate joiner')),
            ("skills_summary",  "🛠️ Skills",          form_data.get('skills_summary',     ', '.join(skills[:8]))),
        ]

        for field_key, label, value in fields:
            col_l, col_v = st.columns([2, 5])
            with col_l:
                st.write(f"**{label}**")
            with col_v:
                st.text_input("", value=str(value),
                    key=f"ff_apply_{field_key}",
                    label_visibility="collapsed")

        st.markdown("---")
        all_data = {label: val for _, label, val in fields}
        st.download_button("📋 Download All Data",
            data=json.dumps(all_data, indent=2),
            file_name="apply_data.json",
            mime="application/json",
            key="apply_download_form_data")

    # ── TAB: Cover Letter ────────────────────────────────────────────────────
    with t2:
        st.subheader("✉️ Cover Letter")
        cover_text = st.text_area("Edit karo",
            value=st.session_state.get('cover_letter', ''),
            height=400,
            key="apply_cover_edit")

        c1, c2, c3 = st.columns(3)
        with c1:
            st.download_button("⬇️ Download", data=cover_text,
                file_name="cover_letter.txt", mime="text/plain",
                type="primary", key="apply_cover_download")
        with c2:
            if st.button("🔄 Regenerate", key="apply_cover_regen"):
                with st.spinner("Regenerating..."):
                    new_cover = generate_cover_letter(
                        st.session_state.get('apply_jd_used', ''), profile, "professional")
                    st.session_state['cover_letter'] = new_cover
                    st.rerun()
        with c3:
            if st.button("💾 Save", key="apply_cover_save"):
                os.makedirs("output", exist_ok=True)
                with open("output/cover_letter.txt", "w") as f:
                    f.write(cover_text)
                st.success("Saved!")

    # ── TAB: Apply Links ─────────────────────────────────────────────────────
    with t3:
        st.subheader("🔗 Direct Apply Links — Indian + Global + Company Pages")

        if pkg.get('apply_url'):
            st.success("✅ Direct Apply Link JD se mila!")
            st.markdown(f"### 🎯 [DIRECT APPLY LINK]({pkg['apply_url']})")
            st.markdown("---")

        links = st.session_state.get('apply_links', {})

        filter_type = st.radio("Platform filter:",
            ["🌟 Sab Dekho", "🇮🇳 Indian Only", "🌐 Global", "💻 Remote", "🏢 Company Pages"],
            horizontal=True, key="apply_link_filter")

        type_map = {
            "🌟 Sab Dekho":     None,
            "🇮🇳 Indian Only":  "indian",
            "🌐 Global":        "global",
            "💻 Remote":        "remote",
            "🏢 Company Pages": "career_page"
        }
        ftype = type_map[filter_type]
        st.markdown("---")

        count = 0
        for platform, info in links.items():
            if ftype and info.get('type') != ftype:
                continue
            quick = "⚡ Quick Apply" if info.get('quick_apply') else "📝 Manual Apply"
            col1, col2, col3 = st.columns([3, 5, 1])
            with col1:
                st.markdown(f"**{platform}**")
                st.caption(f"{quick} • {info.get('description','')}")
            with col2:
                st.text_input("", value=info['url'],
                    key=f"apply_url_field_{count}",
                    label_visibility="collapsed")
            with col3:
                st.markdown(f"[Open ↗]({info['url']})")
            count += 1

        st.caption(f"Total: {count} platforms")

    # ── TAB: Cold Email ──────────────────────────────────────────────────────
    with t4:
        st.subheader("📧 Cold Email to HR")
        email_text = st.text_area("Edit karo",
            value=st.session_state.get('email_template', ''),
            height=320,
            key="apply_email_edit")

        personal = profile.get('personal', profile)
        hr_email = st.text_input("HR Email",
            value=pkg.get('email_to_apply', ''),
            placeholder="hr@company.com",
            key="apply_hr_email")

        c1, c2 = st.columns(2)
        with c1:
            st.download_button("⬇️ Download", data=email_text,
                file_name="cold_email.txt", mime="text/plain",
                type="primary", key="apply_email_download")
        with c2:
            if hr_email:
                subj = f"Application for {pkg.get('job_title','')} — {personal.get('name','')}"
                st.markdown(f"[📨 Open in Email](mailto:{hr_email}?subject={subj.replace(' ','%20')})")

        st.markdown("---")
        st.markdown("**HR Email kahan dhundho:**")
        company = pkg.get('company_name', 'company')
        st.markdown(f"🔍 [Hunter.io](https://hunter.io/search/{company.lower().replace(' ','')})")
        st.markdown(f"🔍 [LinkedIn HR](https://www.linkedin.com/search/results/people/?keywords={company}+recruiter)")

    # ── TAB: Requirements ────────────────────────────────────────────────────
    with t5:
        st.subheader("📊 Job Requirements vs Your Skills")
        r1, r2 = st.columns(2)
        with r1:
            st.markdown("**Job Requirements:**")
            for req in pkg.get('key_requirements', []):
                matched = any(s.lower() in req.lower() or req.lower() in s.lower()
                              for s in skills)
                icon = "✅" if matched else "❌"
                st.write(f"{icon} {req}")
        with r2:
            st.markdown("**Job Info:**")
            for k, v in [
                ("Type",       pkg.get('job_type',             'N/A')),
                ("Experience", pkg.get('experience_required',  'N/A')),
                ("Location",   pkg.get('location',             'N/A')),
                ("Salary",     pkg.get('salary',               'N/A')),
            ]:
                st.write(f"**{k}:** {v}")

    # ── Tracker save ─────────────────────────────────────────────────────────
    st.markdown("---")
    st.subheader("💾 Applied? Tracker mein Save Karo")
    tc1, tc2, tc3 = st.columns(3)
    with tc1:
        tr_title   = st.text_input("Job Title",   value=pkg.get('job_title',    ''), key="apply_tr_title")
    with tc2:
        tr_company = st.text_input("Company",     value=pkg.get('company_name', ''), key="apply_tr_company")
    with tc3:
        tr_url     = st.text_input("URL",         value=pkg.get('apply_url',    ''), key="apply_tr_url")

    if st.button("💾 Save to Tracker", type="primary", key="apply_save_tracker"):
        if tr_title and tr_company:
            from tracker.tracker import mark_applied
            mark_applied(tr_title, tr_company, tr_url, "Applied via Smart Apply")
            st.success(f"✅ Saved: {tr_title} @ {tr_company}")
        else:
            st.error("Title + Company chahiye!")
