"""
Industry-Level ATS Resume Builder — Dashboard Tab
Is file ko dashboard/app.py mein import karo ya seedha tab ke andar paste karo
"""

import streamlit as st
import json
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai.resume_tailor import (
    tailor_resume,
    generate_ats_score,
    parse_existing_resume,
    generate_cover_letter
)


def render_ats_tab(profile: dict):
    """
    Full ATS Resume Builder tab render karo.
    Call: render_ats_tab(profile) inside your tab2 block.
    """

    st.header("📄 Industry-Level ATS Resume Builder")
    st.markdown(
        "Upload your resume → paste JD → get ATS-optimized resume + detailed score report. "
        "Simulates **Workday / Greenhouse / Lever / Taleo** ATS systems."
    )
    st.markdown("---")

    # ── MODE SELECTOR ────────────────────────────────────────────
    mode = st.radio(
        "Mode choose karo:",
        ["🚀 Quick Build (profile.json use karo)",
         "📋 Paste Existing Resume (parse + rebuild)",
         "🎯 Only ATS Score Check (apna resume check karo)"],
        horizontal=True
    )

    st.markdown("---")

    # ── INPUT SECTION ────────────────────────────────────────────
    col_left, col_right = st.columns([1, 1])

    with col_left:
        st.subheader("📋 Job Description")
        jd_input = st.text_area(
            "JD yahan paste karo",
            height=280,
            placeholder="Full job description paste karo — title, requirements, responsibilities sab...",
            key="ats_jd_input"
        )

        if 'last_jd' in st.session_state and st.button("⚡ Last analyzed JD load karo"):
            st.session_state['ats_jd_input_val'] = st.session_state['last_jd']
            st.rerun()

    with col_right:
        if mode == "📋 Paste Existing Resume (parse + rebuild)":
            st.subheader("📄 Your Current Resume")
            existing_resume = st.text_area(
                "Current resume paste karo (any format)",
                height=280,
                placeholder="Apna current resume paste karo — AI parse karke rebuild karega...",
                key="existing_resume_input"
            )
        elif mode == "🎯 Only ATS Score Check (apna resume check karo)":
            st.subheader("📄 Resume to Check")
            check_resume = st.text_area(
                "Resume paste karo jiska ATS score check karna hai",
                height=280,
                placeholder="Resume paste karo...",
                key="check_resume_input"
            )
        else:
            st.subheader("👤 Profile Summary")
            personal = profile.get('personal', {})
            skills = profile.get('skills', [])
            if isinstance(skills, dict):
                all_s = []
                for v in skills.values():
                    if isinstance(v, list):
                        all_s.extend(v)
                skills = all_s

            st.info(f"**Name:** {personal.get('name', 'N/A')}")
            st.info(f"**Skills:** {', '.join(skills[:6])}...")
            exp = profile.get('experience', [])
            if exp:
                st.info(f"**Last Role:** {exp[0].get('title','N/A')} @ {exp[0].get('company','N/A')}")
            proj = profile.get('projects', [])
            if proj:
                st.info(f"**Projects:** {len(proj)} listed")
            st.caption("profile.json se data load ho raha hai. Change karna hai toh profile.json edit karo.")

    # ── GENERATE BUTTON ──────────────────────────────────────────
    st.markdown("---")
    btn_col1, btn_col2, btn_col3 = st.columns(3)
    with btn_col1:
        gen_btn = st.button("🚀 Generate ATS Resume", type="primary", use_container_width=True)
    with btn_col2:
        score_only_btn = st.button("🎯 Check ATS Score Only", use_container_width=True)
    with btn_col3:
        cover_btn = st.button("✉️ Generate Cover Letter", use_container_width=True)

    # ── GENERATE RESUME ──────────────────────────────────────────
    if gen_btn:
        if not jd_input.strip():
            st.error("❌ JD paste karo pehle!")
            return

        active_profile = profile

        if mode == "📋 Paste Existing Resume (parse + rebuild)":
            if not existing_resume.strip():
                st.error("❌ Apna current resume paste karo!")
                return
            with st.spinner("🤖 Resume parse ho raha hai..."):
                parsed_profile = parse_existing_resume(existing_resume)
            if parsed_profile:
                active_profile = parsed_profile
                st.success("✅ Resume parsed! Ab tailoring shuru...")
            else:
                st.warning("⚠️ Parse nahi hua — profile.json use ho raha hai")

        with st.spinner("🤖 AI ATS-optimized resume bana raha hai... (20-30 sec)"):
            resume = tailor_resume(jd_input, active_profile)

        st.session_state['ats_generated_resume'] = resume
        st.session_state['ats_jd_used'] = jd_input
        st.success("✅ ATS Resume ready!")

        # Auto-score
        with st.spinner("🎯 ATS score analyze ho raha hai..."):
            ats_result = generate_ats_score(resume, jd_input)
        st.session_state['ats_score_result'] = ats_result

    # ── SCORE ONLY ───────────────────────────────────────────────
    if score_only_btn:
        resume_to_score = None
        if mode == "🎯 Only ATS Score Check (apna resume check karo)":
            resume_to_score = check_resume if 'check_resume_input' in st.session_state else ""
            if not resume_to_score:
                resume_to_score = st.session_state.get('check_resume_input', '')
        elif 'ats_generated_resume' in st.session_state:
            resume_to_score = st.session_state['ats_generated_resume']
        
        if not resume_to_score or not jd_input.strip():
            st.error("❌ Resume aur JD dono chahiye score check ke liye!")
        else:
            with st.spinner("🎯 ATS systems simulate ho rahi hain..."):
                ats_result = generate_ats_score(resume_to_score, jd_input)
            st.session_state['ats_score_result'] = ats_result
            if 'ats_generated_resume' not in st.session_state and mode == "🎯 Only ATS Score Check (apna resume check karo)":
                st.session_state['ats_generated_resume'] = check_resume

    # ── COVER LETTER ─────────────────────────────────────────────
    if cover_btn:
        if not jd_input.strip():
            st.error("❌ JD paste karo pehle!")
        else:
            tone = st.selectbox("Tone:", ["professional", "conversational", "enthusiastic"], key="cl_tone")
            with st.spinner("✉️ Cover letter likh raha hai..."):
                cl = generate_cover_letter(jd_input, profile, tone)
            st.session_state['cover_letter'] = cl

    # ════════════════════════════════════════════════════════════
    # OUTPUT SECTION
    # ════════════════════════════════════════════════════════════

    if 'ats_generated_resume' in st.session_state:
        st.markdown("---")
        st.subheader("📄 Your ATS-Optimized Resume")

        resume_text = st.session_state['ats_generated_resume']

        # Edit + Preview
        out_col1, out_col2 = st.columns([1, 1])
        with out_col1:
            st.markdown("**✏️ Edit Resume:**")
            edited = st.text_area("", value=resume_text, height=500, key="editable_ats_resume")

        with out_col2:
            st.markdown("**👁️ Formatted Preview:**")
            preview_container = st.container()
            with preview_container:
                for line in resume_text.split('\n'):
                    if not line.strip():
                        st.write("")
                    elif line.strip().startswith('─') or line.strip().startswith('═'):
                        st.markdown("<hr style='margin:4px 0; border-color:#444'>", unsafe_allow_html=True)
                    elif (line.strip().isupper() and len(line.strip()) > 3
                          and not line.strip().startswith('•')):
                        st.markdown(f"<b style='font-size:15px; color:#1a73e8'>{line.strip()}</b>",
                                    unsafe_allow_html=True)
                    elif line.strip().startswith('•'):
                        st.markdown(f"<span style='color:#333'>  {line.strip()}</span>",
                                    unsafe_allow_html=True)
                    else:
                        st.markdown(f"<span style='color:#222'>{line}</span>",
                                    unsafe_allow_html=True)

        # Download buttons
        dl_col1, dl_col2, dl_col3 = st.columns(3)
        final_resume = edited if edited else resume_text
        with dl_col1:
            st.download_button("⬇️ Download TXT", data=final_resume,
                               file_name="ats_resume.txt", mime="text/plain",
                               type="primary", use_container_width=True)
        with dl_col2:
            if st.button("💾 Save to output/", use_container_width=True):
                os.makedirs("output", exist_ok=True)
                with open("output/latest_ats_resume.txt", "w") as f:
                    f.write(final_resume)
                st.success("✅ output/latest_ats_resume.txt")
        with dl_col3:
            if st.button("🔄 Re-check ATS Score", use_container_width=True):
                jd_check = st.session_state.get('ats_jd_used', jd_input)
                with st.spinner("ATS re-analyzing..."):
                    new_score = generate_ats_score(final_resume, jd_check)
                st.session_state['ats_score_result'] = new_score

    # ════════════════════════════════════════════════════════════
    # ATS SCORE REPORT
    # ════════════════════════════════════════════════════════════

    if 'ats_score_result' in st.session_state:
        ats = st.session_state['ats_score_result']
        st.markdown("---")
        st.subheader("🎯 ATS Analysis Report")
        st.caption("Simulating: Workday · Greenhouse · Lever · Taleo · iCIMS")

        # ── VERDICT BANNER ────────────────────────────────────
        verdict = ats.get('ats_verdict', 'BORDERLINE')
        verdict_colors = {
            "HIGHLY_LIKELY_TO_PASS": ("success", "🟢 HIGHLY LIKELY TO PASS ATS"),
            "LIKELY_TO_PASS":        ("success", "🟡 LIKELY TO PASS ATS"),
            "BORDERLINE":            ("warning", "⚠️ BORDERLINE — Improvement Needed"),
            "LIKELY_TO_FAIL":        ("error",   "🔴 LIKELY TO FAIL ATS — Fix Urgently"),
        }
        color_fn, verdict_label = verdict_colors.get(verdict, ("warning", verdict))
        getattr(st, color_fn)(f"**{verdict_label}**")
        if ats.get('verdict_reason'):
            st.caption(ats['verdict_reason'])

        # ── SCORE METERS ─────────────────────────────────────
        sc1, sc2, sc3, sc4, sc5 = st.columns(5)
        scores = [
            (sc1, "🏆 ATS Score",        ats.get('overall_ats_score', 0),         "overall"),
            (sc2, "🔑 Keyword Match",     ats.get('keyword_match_score', 0),       "keyword"),
            (sc3, "📐 Format Score",      ats.get('format_score', 0),              "format"),
            (sc4, "📝 Content Quality",   ats.get('content_quality_score', 0),     "content"),
            (sc5, "📋 Sections Complete", ats.get('section_completeness_score', 0), "sections"),
        ]
        for col, label, val, key in scores:
            with col:
                color = "#22c55e" if val >= 80 else "#f59e0b" if val >= 60 else "#ef4444"
                st.markdown(
                    f"""<div style="text-align:center; padding:12px; border-radius:10px;
                    border:2px solid {color}; background:{color}18">
                    <div style="font-size:28px; font-weight:700; color:{color}">{val}%</div>
                    <div style="font-size:11px; color:#555; margin-top:4px">{label}</div>
                    </div>""",
                    unsafe_allow_html=True
                )

        st.markdown("&nbsp;", unsafe_allow_html=True)

        # ── BREAKDOWN ─────────────────────────────────────────
        breakdown = ats.get('score_breakdown', {})
        if breakdown:
            st.markdown("**📊 Detailed Breakdown:**")
            b_cols = st.columns(5)
            bd_items = [
                ("Hard Skills",   breakdown.get('hard_skills_match', 0)),
                ("Soft Skills",   breakdown.get('soft_skills_match', 0)),
                ("Exp Relevance", breakdown.get('experience_relevance', 0)),
                ("Education",     breakdown.get('education_match', 0)),
                ("Keyword Density", breakdown.get('keyword_density', 0)),
            ]
            for col, (label, val) in zip(b_cols, bd_items):
                with col:
                    st.progress(val / 100, text=f"{label}: {val}%")

        st.markdown("---")

        # ── KEYWORDS ──────────────────────────────────────────
        kw_col1, kw_col2, kw_col3 = st.columns(3)
        with kw_col1:
            st.markdown("**✅ Matched Keywords**")
            matched = ats.get('matched_keywords', [])
            for kw in matched:
                st.markdown(f"🟢 `{kw}`")

        with kw_col2:
            st.markdown("**🔴 Missing Critical Keywords**")
            missing = ats.get('missing_critical_keywords', [])
            for kw in missing:
                st.markdown(f"🔴 `{kw}`")

        with kw_col3:
            st.markdown("**🟡 Nice-to-Have (Missing)**")
            nth = ats.get('missing_nice_to_have', [])
            for kw in nth:
                st.markdown(f"🟡 `{kw}`")

        st.markdown("---")

        # ── SECTIONS CHECK ────────────────────────────────────
        sa = ats.get('section_analysis', {})
        if sa:
            st.markdown("**📋 Resume Sections Checklist:**")
            sec_cols = st.columns(9)
            section_labels = [
                ("Summary",       "has_summary"),
                ("Skills",        "has_skills"),
                ("Experience",    "has_experience"),
                ("Education",     "has_education"),
                ("Projects",      "has_projects"),
                ("Certifications","has_certifications"),
                ("Contact",       "has_contact_info"),
                ("LinkedIn",      "has_linkedin"),
                ("GitHub",        "has_github"),
            ]
            for col, (label, key) in zip(sec_cols, section_labels):
                with col:
                    present = sa.get(key, False)
                    st.markdown(
                        f"<div style='text-align:center; font-size:11px'>"
                        f"{'✅' if present else '❌'}<br>{label}</div>",
                        unsafe_allow_html=True
                    )

        st.markdown("---")

        # ── INSIGHTS ──────────────────────────────────────────
        ins_col1, ins_col2, ins_col3 = st.columns(3)
        with ins_col1:
            st.markdown("**💪 Strengths**")
            for s in ats.get('strengths', []):
                st.markdown(f"⭐ {s}")

        with ins_col2:
            st.markdown("**💡 Improvements**")
            for imp in ats.get('content_improvements', []):
                st.markdown(f"📝 {imp}")

        with ins_col3:
            st.markdown("**⚠️ Format Issues**")
            for fi in ats.get('format_issues', []):
                st.markdown(f"⚠️ {fi}")

        # ── TOP 3 ACTIONS ─────────────────────────────────────
        top3 = ats.get('top_3_actions', [])
        if top3:
            st.markdown("---")
            st.markdown("**🎯 Top 3 Actions Right Now:**")
            for i, action in enumerate(top3, 1):
                priority_color = ["#ef4444", "#f59e0b", "#22c55e"][i - 1]
                st.markdown(
                    f"""<div style="padding:10px 16px; margin:6px 0; border-radius:8px;
                    border-left:4px solid {priority_color}; background:{priority_color}12">
                    <b style="color:{priority_color}">#{i}</b> {action}</div>""",
                    unsafe_allow_html=True
                )

        # ── MISC ──────────────────────────────────────────────
        misc_col1, misc_col2, misc_col3 = st.columns(3)
        with misc_col1:
            exp_match = ats.get('experience_match', 'N/A')
            color = "#22c55e" if exp_match == "matched" else "#f59e0b"
            st.markdown(f"**Experience Fit:** <span style='color:{color}'>{exp_match.upper()}</span>",
                        unsafe_allow_html=True)
        with misc_col2:
            prob = ats.get('estimated_interview_probability', 'N/A')
            st.markdown(f"**Interview Probability:** `{prob.upper()}`")
        with misc_col3:
            role = ats.get('jd_role', 'N/A')
            st.markdown(f"**Role Detected:** `{role}`")

    # ── COVER LETTER OUTPUT ──────────────────────────────────────
    if 'cover_letter' in st.session_state:
        st.markdown("---")
        st.subheader("✉️ Tailored Cover Letter")
        cl_text = st.text_area("Cover Letter (edit karo):", value=st.session_state['cover_letter'],
                               height=300, key="cl_display")
        st.download_button("⬇️ Download Cover Letter", data=cl_text,
                           file_name="cover_letter.txt", mime="text/plain")