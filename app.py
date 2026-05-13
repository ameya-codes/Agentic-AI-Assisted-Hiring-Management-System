"""
Agentic AI Assisted Hiring Management System — Streamlit POC
Run: streamlit run app.py
"""

from __future__ import annotations

from pathlib import Path

try:
    from dotenv import load_dotenv

    load_dotenv(Path(__file__).resolve().parent / ".env")
except ImportError:
    pass

from datetime import date, datetime

import pandas as pd
import streamlit as st

import db
import mock_ai
import ui_theme as ui

st.set_page_config(
    page_title="HireFlow AI · Hiring",
    page_icon="briefcase",
    layout="wide",
    initial_sidebar_state="expanded",
)

ROLES = [
    "Hiring Manager",
    "HR Recruiter",
    "Candidate",
    "Interviewer",
]

STATUS_OPTIONS = [
    "New",
    "Shortlisted",
    "Interview Scheduled",
    "Interview Completed",
    "Offer Generated",
    "Onboarded",
    "Rejected",
]

OFFER_STATUS_OPTIONS = ["Draft", "Pending HR Approval", "Approved", "Sent"]


def init_app_data():
    db.init_db()
    db.seed_if_empty()


def badge_html(status: str) -> str:
    palette = {
        "New": ("#475569", "#f1f5f9"),
        "Shortlisted": ("#1d4ed8", "#dbeafe"),
        "Interview Scheduled": ("#6d28d9", "#ede9fe"),
        "Interview Completed": ("#0369a1", "#e0f2fe"),
        "Offer Generated": ("#b45309", "#fef3c7"),
        "Onboarded": ("#047857", "#d1fae5"),
        "Rejected": ("#b91c1c", "#fee2e2"),
        "Draft": ("#475569", "#f1f5f9"),
        "Pending HR Approval": ("#c2410c", "#ffedd5"),
        "Approved": ("#047857", "#d1fae5"),
        "Sent": ("#1e40af", "#dbeafe"),
        "Open": ("#047857", "#d1fae5"),
    }
    fg, bg = palette.get(status, ("#0f172a", "#f1f5f9"))
    return (
        f'<span style="display:inline-block;padding:3px 10px;border-radius:999px;'
        f'font-size:11px;font-weight:600;color:{fg};background:{bg};border:1px solid rgba(15,23,42,.06);">'
        f"{status}</span>"
    )


def role_can_edit_pipeline() -> bool:
    r = st.session_state.get("role")
    return r in ("HR Recruiter", "Hiring Manager")


def role_can_screen() -> bool:
    return st.session_state.get("role") == "HR Recruiter"


def role_can_schedule() -> bool:
    return st.session_state.get("role") in ("HR Recruiter", "Hiring Manager")


def role_can_feedback() -> bool:
    return st.session_state.get("role") in ("Interviewer", "HR Recruiter")


def role_can_offer() -> bool:
    return st.session_state.get("role") == "HR Recruiter"


def require_role():
    if not st.session_state.get("role"):
        st.warning("Session expired — sign in again.")
        st.stop()


def render_login() -> None:
    st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)
    left, right = st.columns([1.2, 1], gap="large")
    with left:
        ui.login_hero_column()
    with right:
        with st.container(border=True):
            st.caption("DEMO ENVIRONMENT")
            ui.login_card_headers()
            role = st.selectbox(
                "Role",
                ["Choose a role…"] + ROLES,
                label_visibility="collapsed",
                key="login_role_select",
            )
            if st.button("Continue", type="primary", use_container_width=True):
                if role == "Choose a role…":
                    st.error("Select a role to continue.")
                else:
                    st.session_state["role"] = role
                    db.log_audit("LOGIN", "session", None, role, "Role selected for demo session.")
                    st.rerun()


def page_dashboard():
    role = st.session_state.get("role", "")
    ui.page_header(
        "Overview",
        "Pipeline health and audit trail — same view leadership sees in weekly hiring reviews."
        if role != "Candidate"
        else "Organization snapshot (demo). In production this would be personalized to your applications.",
        kicker="Dashboard",
    )
    ui.poc_note()
    require_role()
    stats = db.dashboard_stats()
    ui.metrics_row(stats)

    with st.container(border=True):
        ui.section_heading("Pipeline by stage")
        pipe = [{"Stage": r["status"], "Headcount": r["cnt"]} for r in stats["pipeline"]]
        if pipe:
            df = pd.DataFrame(pipe)
            st.bar_chart(df.set_index("Stage"))
            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Stage": st.column_config.TextColumn("Stage"),
                    "Headcount": st.column_config.NumberColumn("Count", format="%d"),
                },
            )
        else:
            st.caption("No candidates yet.")

    with st.container(border=True):
        ui.section_heading("Recent audit events")
        logs = db.recent_audit(12)
        if logs:
            st.dataframe(
                pd.DataFrame([dict(x) for x in logs]),
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.caption("No audit entries.")


def page_candidate_portal():
    ui.page_header(
        "Candidate portal",
        "Open roles and how your application would progress through screening and interviews.",
        kicker="Candidate experience",
    )
    ui.poc_note()
    require_role()

    with st.container(border=True):
        ui.section_heading("Open requisitions")
        jobs = db.list_jobs()
        if jobs:
            rows = [
                {
                    "Title": j["title"],
                    "Team": j["department"],
                    "Location": j["location"],
                    "Band": f"${j['salary_min']:,.0f} – ${j['salary_max']:,.0f}",
                    "Status": j["status"],
                }
                for j in jobs
            ]
            st.dataframe(
                pd.DataFrame(rows),
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.caption("No open roles.")

    with st.container(border=True):
        ui.section_heading("What happens next")
        st.markdown(
            """
1. **Intake** — HR screens your profile against the role.  
2. **Pipeline** — Hiring team shortlists and schedules structured interviews.  
3. **Decision** — Interviewers record feedback; hiring manager and HR align on offer.  
4. **Onboarding** — After approval, tasks and provisioning follow a standard checklist.

*This demo does not store a real “my application” identity; it illustrates the enterprise stages.*
            """.strip()
        )


def page_job_requisition():
    ui.page_header(
        "Job requisitions",
        "Create and publish reqs with AI-assisted drafting and policy notes.",
        kicker="Workforce planning",
    )
    ui.poc_note()
    require_role()
    if st.session_state.get("role") not in ("Hiring Manager", "HR Recruiter"):
        st.warning("Your role would not typically create requisitions in a live HRIS.")

    with st.container(border=True):
        ui.section_heading("Create requisition")
        with st.form("job_form"):
            c1, c2 = st.columns(2)
            title = c1.text_input("Job title", "Software Engineer II")
            department = c2.text_input("Department", "Engineering")
            location = st.text_input("Location", "Hybrid — Austin, TX")
            r1, r2 = st.columns(2)
            salary_min = r1.number_input("Salary min (USD)", min_value=0, value=120000, step=5000)
            salary_max = r2.number_input("Salary max (USD)", min_value=0, value=155000, step=5000)
            experience = st.selectbox("Experience level", ["Intern", "Junior", "Mid", "Senior", "Staff"])
            skills = st.text_input("Required skills (comma-separated)", "Python, SQL, APIs, AWS")
            desc = st.text_area("Job description", height=140, placeholder="Paste a draft or generate with AI.")
            b1, b2 = st.columns(2)
            gen = b1.form_submit_button("Generate with AI")
            save = b2.form_submit_button("Publish requisition", type="primary")

        if gen:
            out = mock_ai.generate_job_description(
                title, department, location, float(salary_min), float(salary_max), experience, skills, notes=desc
            )
            st.session_state["last_job_ai"] = out
            st.success("Draft ready — review agent output, then publish when satisfied.")
            with st.expander("Job description agent — output", expanded=True):
                st.markdown(out["description"])
            with st.expander("Skills, bias check, and improvements"):
                st.markdown("**Recommended skills:** " + out["recommended_skills"])
                st.markdown("**Bias check:** " + out["bias_check"])
                st.markdown("**Improvements:**\n" + out["improvements"])

        if save:
            payload = {
                "title": title,
                "department": department,
                "location": location,
                "salary_min": float(salary_min),
                "salary_max": float(salary_max),
                "experience_level": experience,
                "required_skills": skills,
                "description": desc
                or (
                    st.session_state.get("last_job_ai", {}).get("description")
                    if st.session_state.get("last_job_ai")
                    else ""
                ),
            }
            jid = db.insert_job(payload)
            db.log_audit("CREATE_JOB", "jobs", jid, st.session_state["role"], f"Created job: {title}")
            st.success(f"Requisition **#{jid}** saved.")

    with st.container(border=True):
        ui.section_heading("Published requisitions")
        jobs = db.list_jobs()
        if jobs:
            st.dataframe(
                pd.DataFrame(
                    [
                        {
                            "ID": j["id"],
                            "Title": j["title"],
                            "Department": j["department"],
                            "Location": j["location"],
                            "Compensation": f"${j['salary_min']:,.0f} – ${j['salary_max']:,.0f}",
                            "Status": j["status"],
                        }
                        for j in jobs
                    ]
                ),
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.caption("No jobs yet.")


def page_resume_screening():
    ui.page_header(
        "Resume screening",
        "Intake queue with structured AI signals for recruiter review.",
        kicker="Talent acquisition",
    )
    ui.poc_note()
    require_role()
    if not role_can_screen():
        st.info("Switch to **HR Recruiter** to mirror who owns intake in most organizations.")

    jobs = db.list_jobs()
    if not jobs:
        st.warning("Create a requisition first.")
        return

    job_labels = {f"{j['id']} — {j['title']} ({j['department']})": j for j in jobs}
    with st.container(border=True):
        ui.section_heading("Screen candidate")
        choice = st.selectbox("Requisition", list(job_labels.keys()))
        job = job_labels[choice]
        n1, n2 = st.columns(2)
        name = n1.text_input("Full name", "Jamie Doe")
        email = n2.text_input("Email", "jamie.doe@example.com")
        resume_text = st.text_area("Resume text", height=160, help="Paste text or upload .txt below.")
        uploaded = st.file_uploader("Upload resume (.txt)", type=["txt"])
        if uploaded is not None:
            resume_text = uploaded.read().decode("utf-8", errors="replace")

        if st.button("Run AI screening", type="primary"):
            if not resume_text.strip():
                st.error("Add resume content.")
            else:
                screening = mock_ai.screen_resume(resume_text, job["required_skills"] or "", job["title"] or "")
                st.session_state["pending_screening"] = screening
                st.session_state["pending_resume_meta"] = {
                    "job_id": job["id"],
                    "name": name,
                    "email": email,
                    "resume_text": resume_text,
                }
                st.success("Screening package ready for review.")
                a, b, c = st.columns(3)
                a.metric("Match score", f"{screening['match_score']}/100")
                b.metric("Recommendation", screening["recommendation"])
                c.metric("Role", job["title"])
                ui.section_heading("Profile extraction")
                st.write(
                    {
                        "Skills": screening["skills"],
                        "Experience": screening["experience"],
                        "Education": screening["education"],
                        "Certifications": screening["certifications"],
                        "Strengths": screening["strengths"],
                        "Gaps / risks": screening["weaknesses"],
                    }
                )

        if st.session_state.get("pending_screening") and st.session_state.get("pending_resume_meta"):
            if st.button("Commit to ATS record"):
                meta = st.session_state["pending_resume_meta"]
                cid = db.insert_candidate_screening(
                    meta["job_id"],
                    meta["name"],
                    meta["email"],
                    meta["resume_text"],
                    st.session_state["pending_screening"],
                )
                db.log_audit(
                    "SCREEN_RESUME",
                    "candidates",
                    cid,
                    st.session_state.get("role", "unknown"),
                    f"Saved screening for {meta['name']}",
                )
                st.session_state.pop("pending_screening", None)
                st.session_state.pop("pending_resume_meta", None)
                st.success(f"Candidate **#{cid}** saved.")


def page_ranking():
    ui.page_header(
        "Candidate pipeline",
        "Ranked queue with AI-assisted scoring — human approval for every stage change.",
        kicker="Recruiting operations",
    )
    ui.poc_note()
    require_role()

    rows = db.ranked_candidates()
    if not rows:
        st.caption("No candidates yet.")
        return

    base = [dict(r) for r in rows]
    ranked = mock_ai.rank_candidates(base)
    table = []
    for r in ranked:
        table.append(
            {
                "Rank": r["rank"],
                "Candidate": r["name"],
                "Role": r["job_title"],
                "Match": r["match_score"],
                "Skills (excerpt)": (r["skills"] or "")[:100],
                "AI recommendation": r["recommendation"],
                "Workflow status": r["status"],
                "candidate_id": r["candidate_id"],
            }
        )
    df = pd.DataFrame(table)
    show = df.drop(columns=["candidate_id"])

    with st.container(border=True):
        ui.section_heading("Pipeline board")
        st.dataframe(show, use_container_width=True, hide_index=True)

    with st.container(border=True):
        ui.section_heading("Human approval — status change")
        if not role_can_edit_pipeline():
            st.warning("Only **Hiring Manager** or **HR Recruiter** may advance candidates in this demo.")
            return
        ids = df["candidate_id"].tolist()
        labels = [f"{cid} — {df.loc[df['candidate_id']==cid,'Candidate'].iloc[0]}" for cid in ids]
        pick = st.selectbox("Candidate", ids, format_func=lambda x: labels[ids.index(x)])
        cur_status = df.loc[df["candidate_id"] == pick, "Workflow status"].iloc[0]
        try:
            idx = STATUS_OPTIONS.index(cur_status)
        except ValueError:
            idx = 0
        new_status = st.selectbox("Target status", STATUS_OPTIONS, index=idx)
        if st.button("Apply update", type="primary"):
            db.update_candidate_status(pick, new_status)
            db.log_audit(
                "STATUS_CHANGE",
                "candidates",
                pick,
                st.session_state["role"],
                f"Status -> {new_status}",
            )
            st.success("Pipeline updated.")
            st.rerun()


def page_interview_schedule():
    ui.page_header(
        "Interview scheduling",
        "Coordinate panels, comms drafts, and structured question banks.",
        kicker="Coordination",
    )
    ui.poc_note()
    require_role()
    if not role_can_schedule():
        st.info("Scheduling is limited to **Hiring Manager** and **HR Recruiter** in this demo.")

    shorts = db.shortlisted_candidates()
    if not shorts:
        st.warning("Shortlist at least one candidate before scheduling.")
        return

    opts = {f"{s['id']} — {s['name']} ({s['job_title']})": s for s in shorts}
    with st.container(border=True):
        ui.section_heading("Schedule session")
        pick = st.selectbox("Candidate", list(opts.keys()))
        cand = opts[pick]
        interviewer = st.text_input("Interviewer", "Jamie Ortiz")
        dt = st.datetime_input("Start time", value=datetime(2026, 5, 20, 14, 0))
        itype = st.selectbox("Interview type", ["Technical", "Behavioral", "Final"])

        resume_snippet = ""
        with db.get_conn() as conn:
            row = conn.execute("SELECT resume_text FROM candidates WHERE id = ?", (cand["id"],)).fetchone()
            if row:
                resume_snippet = row["resume_text"] or ""

        if st.button("Generate invitation & question bank"):
            when = dt.strftime("%Y-%m-%d %H:%M")
            email = mock_ai.generate_interview_email(
                cand["name"], cand["job_title"], interviewer, when, itype
            )
            qs = mock_ai.generate_interview_questions(cand["job_title"], itype, resume_snippet)
            st.session_state["sched_ai"] = {
                "email": email,
                "tech": qs["technical"],
                "beh": qs["behavioral"],
                "when": when,
            }
            st.success("Drafts generated — review before sending.")
            st.text_area("Invitation email", email, height=180)
            st.text_area("Technical prompts", qs["technical"], height=140)
            st.text_area("Behavioral prompts", qs["behavioral"], height=140)

        if st.button("Save to calendar & ATS", type="primary"):
            pack = st.session_state.get("sched_ai")
            if not pack:
                when = dt.strftime("%Y-%m-%d %H:%M")
                email = mock_ai.generate_interview_email(
                    cand["name"], cand["job_title"], interviewer, when, itype
                )
                qs = mock_ai.generate_interview_questions(cand["job_title"], itype, resume_snippet)
            else:
                when, email = pack["when"], pack["email"]
                qs = {"technical": pack["tech"], "behavioral": pack["beh"]}
            iid = db.insert_interview(
                {
                    "candidate_id": cand["id"],
                    "interviewer_name": interviewer,
                    "scheduled_at": when,
                    "interview_type": itype,
                    "invitation_email": email,
                    "tech_questions": qs["technical"],
                    "behavioral_questions": qs["behavioral"],
                }
            )
            db.update_candidate_status(cand["id"], "Interview Scheduled")
            db.log_audit("SCHEDULE_INTERVIEW", "interviews", iid, st.session_state["role"], f"candidate {cand['id']}")
            st.success(f"Interview **#{iid}** recorded.")


def page_feedback():
    ui.page_header(
        "Interview feedback",
        "Structured debrief with AI synthesis for HRBP / HM readout.",
        kicker="Decision support",
    )
    ui.poc_note()
    require_role()
    if not role_can_feedback():
        st.warning("Feedback entry is enabled for **Interviewer** and **HR Recruiter**.")

    ivs = db.list_interviews_for_feedback()
    pending = [dict(x) for x in ivs if x["has_feedback"] == 0]

    with st.container(border=True):
        ui.section_heading("Submit debrief")
        if not pending:
            st.info("No sessions awaiting feedback.")
        else:
            labels = {
                f"{p['id']} — {p['candidate_name']} · {p['interview_type']} · {p['scheduled_at']}": p
                for p in pending
            }
            choice = st.selectbox("Interview", list(labels.keys()))
            row = labels[choice]
            tech = st.text_area("Technical assessment", "Solid depth on API design and reliability tradeoffs.")
            comm = st.text_area("Communication & leadership signals", "Clear structure; strong stakeholder empathy.")
            rating = st.slider("Overall score (1–5)", 1, 5, 4)
            decision = st.selectbox("Recommendation", ["Hire", "No Hire", "Maybe"])

            if st.button("Generate HR-facing summary"):
                out = mock_ai.summarize_feedback(tech, comm, rating, decision)
                st.session_state["fb_ai"] = out
                st.markdown(f"**Summary:** {out['summary']}")
                st.markdown(f"**Sentiment:** {out['sentiment']}")
                st.markdown(f"**Strengths:** {out['strengths']}")
                st.markdown(f"**Risks:** {out['risks']}")
                st.markdown(f"**Recommendation:** {out['final_recommendation']}")

            if st.button("Submit to ATS", type="primary"):
                out = st.session_state.get("fb_ai") or mock_ai.summarize_feedback(tech, comm, rating, decision)
                fid = db.insert_feedback(
                    {
                        "interview_id": row["id"],
                        "technical_feedback": tech,
                        "communication_feedback": comm,
                        "overall_rating": rating,
                        "hire_decision": decision,
                        "ai_summary": out["summary"],
                        "sentiment": out["sentiment"],
                        "candidate_strengths": out["strengths"],
                        "candidate_risks": out["risks"],
                        "final_recommendation": out["final_recommendation"],
                    }
                )
                db.update_candidate_status(row["candidate_id"], "Interview Completed")
                db.log_audit("FEEDBACK", "feedback", fid, st.session_state["role"], f"interview {row['id']}")
                st.session_state.pop("fb_ai", None)
                st.success("Feedback submitted.")

    with st.container(border=True):
        ui.section_heading("Recent submissions")
        with db.get_conn() as conn:
            fb_rows = conn.execute(
                """
                SELECT f.id, f.hire_decision, f.overall_rating, f.sentiment, c.name AS candidate_name,
                       i.interview_type, f.created_at
                FROM feedback f
                JOIN interviews i ON i.id = f.interview_id
                JOIN candidates c ON c.id = i.candidate_id
                ORDER BY f.id DESC
                LIMIT 20
                """
            ).fetchall()
        if fb_rows:
            st.dataframe(
                pd.DataFrame([dict(x) for x in fb_rows]),
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.caption("No records.")


def page_offer():
    ui.page_header(
        "Offers & approvals",
        "Compensation and approval chain stay explicitly human-controlled.",
        kicker="Total rewards",
    )
    ui.poc_note()
    require_role()

    pool = db.candidates_for_offer()
    with st.container(border=True):
        ui.section_heading("New offer package")
        if not pool:
            st.caption("No candidates with Hire / Maybe feedback — complete interviews first.")
        elif not role_can_offer():
            st.info("Drafting new offers is limited to **HR Recruiter** in this demo.")
        else:
            opts = {f"{p['id']} — {p['name']} ({p['job_title']}) · {p['hire_decision']}": p for p in pool}
            pick = st.selectbox("Select hire-ready candidate", list(opts.keys()))
            cand = opts[pick]
            salary = st.number_input("Base salary (USD)", min_value=0.0, value=125000.0, step=1000.0)
            start = st.date_input("Target start date", value=date(2026, 6, 16))
            title = st.text_input("Title on letter", cand["job_title"])
            mgr = st.text_input("Reports to", "Alex Rivera — Engineering Manager")

            if st.button("Generate letter draft"):
                letter = mock_ai.generate_offer_letter(cand["name"], title, salary, str(start), mgr)
                st.session_state["offer_letter"] = letter
                st.text_area("Preview", letter, height=240)

            if st.button("Save as draft in ATS", type="primary"):
                letter = st.session_state.get("offer_letter") or mock_ai.generate_offer_letter(
                    cand["name"], title, salary, str(start), mgr
                )
                oid = db.insert_offer(
                    {
                        "candidate_id": cand["id"],
                        "salary": salary,
                        "start_date": str(start),
                        "job_title": title,
                        "reporting_manager": mgr,
                        "letter_text": letter,
                        "approval_status": "Draft",
                    }
                )
                db.update_candidate_status(cand["id"], "Offer Generated")
                db.log_audit("OFFER_DRAFT", "offers", oid, st.session_state["role"], f"candidate {cand['id']}")
                st.success(f"Offer **#{oid}** stored as draft.")

    with st.container(border=True):
        ui.section_heading("Approval queue")
        offers = db.list_offers()
        if not offers:
            st.caption("No offers.")
        elif role_can_offer():
            for o in offers:
                cols = st.columns([2, 1, 1, 1])
                cols[0].markdown(f"**{o['candidate_name']}** · Offer #{o['id']}")
                cols[1].markdown(badge_html(o["approval_status"]), unsafe_allow_html=True)
                cols[2].markdown(f"**${o['salary']:,.0f}**")
                cur = o["approval_status"] if o["approval_status"] in OFFER_STATUS_OPTIONS else "Draft"
                new_s = cols[3].selectbox(
                    "State",
                    OFFER_STATUS_OPTIONS,
                    index=OFFER_STATUS_OPTIONS.index(cur),
                    key=f"offerstat_{o['id']}",
                    label_visibility="collapsed",
                )
                if st.button("Update", key=f"btn_offer_{o['id']}"):
                    db.update_offer_status(o["id"], new_s)
                    if new_s in ("Approved", "Sent"):
                        db.update_candidate_status(o["candidate_id"], "Offer Generated")
                    db.log_audit("OFFER_STATUS", "offers", o["id"], st.session_state["role"], new_s)
                    st.rerun()
        else:
            for o in offers:
                st.markdown(
                    f"{o['candidate_name']} · #{o['id']} · {badge_html(o['approval_status'])} · "
                    f"${o['salary']:,.0f}",
                    unsafe_allow_html=True,
                )


def page_onboarding():
    ui.page_header(
        "Onboarding",
        "Checklist and assistant for post-offer / Day-0 readiness.",
        kicker="People operations",
    )
    ui.poc_note()
    require_role()
    if st.session_state.get("role") != "HR Recruiter":
        st.info("Primary ownership is **HR Recruiter** — you can still read along in this POC.")

    people = db.onboarding_candidates()
    if not people:
        st.warning("Requires an offer in **Approved** or **Sent** state.")
        return

    labels = {f"{p['id']} — {p['name']} ({p['approval_status']})": p for p in people}
    pick = st.selectbox("New hire", list(labels.keys()))
    cid = labels[pick]["id"]

    with st.container(border=True):
        ui.section_heading("Task checklist")
        tasks = db.get_onboarding_tasks(cid)
        for t in tasks:
            done = st.checkbox(t["task_name"], value=bool(t["completed"]), key=f"task_{t['id']}")
            if done != bool(t["completed"]):
                db.toggle_onboarding_task(t["id"], 1 if done else 0)
                db.log_audit("ONBOARD_TASK", "onboarding_tasks", t["id"], st.session_state["role"], t["task_name"])

    with st.container(border=True):
        ui.section_heading("Onboarding assistant")
        q = st.text_input("Question for policy bot", "When will I receive my laptop?")
        if st.button("Get guidance"):
            st.info(mock_ai.onboarding_chatbot_response(q))


def page_architecture():
    ui.page_header(
        "Agents & governance",
        "How automation is bounded in an enterprise-grade hiring stack.",
        kicker="Platform",
    )
    ui.poc_note()
    agents = [
        ("Job Description Generation", "Inclusive drafts, skill suggestions, bias checks."),
        ("Resume Screening", "Structured extraction + match score."),
        ("Candidate Ranking", "Ordered work queue for recruiters."),
        ("Interview Scheduling", "Logistics + calendar-ready drafts."),
        ("Communications", "Candidate-facing email templates."),
        ("Interview Questions", "Role-calibrated technical / behavioral banks."),
        ("Feedback Synthesis", "HR-ready summary from interviewer notes."),
        ("Offer Generation", "Letter drafting from approved comp facts."),
        ("Onboarding Assistant", "FAQ from handbook snippets."),
    ]
    with st.container(border=True):
        ui.section_heading("Agent roster")
        st.dataframe(
            pd.DataFrame(agents, columns=["Agent", "Responsibility"]),
            use_container_width=True,
            hide_index=True,
        )

    with st.container(border=True):
        ui.section_heading("Explicitly human-owned")
        st.markdown(
            """
- Final hiring decision and exec calibration  
- **Salary bands and individual comp approval**  
- Legal review of offers and regional compliance  
- HR investigations, conflicts, accommodations  
- **Background check adjudication**  
            """.strip()
        )

    with st.container(border=True):
        ui.section_heading("Reference architecture")
        st.code(
            "Workday / Greenhouse-style ATS UI\n  → Policy & approvals (RBAC)\n  → Agent services (LLM + guardrails)\n  → System of record (HRIS / data warehouse)\n\nThis POC: Streamlit + SQLite + mock agents",
            language="text",
        )


# (nav_key, sidebar label, handler, allowed_roles or None for all authenticated)
NAV_DEF: list[tuple[str, str, object, frozenset[str] | None]] = [
    ("overview", "Overview", page_dashboard, None),
    ("requisitions", "Job requisitions", page_job_requisition, frozenset({"Hiring Manager", "HR Recruiter"})),
    ("screening", "Resume screening", page_resume_screening, frozenset({"HR Recruiter"})),
    ("pipeline", "Candidate pipeline", page_ranking, frozenset({"Hiring Manager", "HR Recruiter"})),
    ("interviews", "Interviews", page_interview_schedule, frozenset({"Hiring Manager", "HR Recruiter"})),
    ("feedback", "Interview feedback", page_feedback, frozenset({"Interviewer", "HR Recruiter"})),
    ("offers", "Offers & approvals", page_offer, frozenset({"Hiring Manager", "HR Recruiter"})),
    ("onboarding", "Onboarding", page_onboarding, frozenset({"HR Recruiter"})),
    ("candidate", "Candidate portal", page_candidate_portal, frozenset({"Candidate"})),
    ("agents", "Agents & governance", page_architecture, None),
]


def nav_items_for_role(role: str) -> list[tuple[str, str, object]]:
    out = []
    for key, label, fn, allowed in NAV_DEF:
        if allowed is None or role in allowed:
            out.append((key, label, fn))
    return out


def main():
    init_app_data()
    role = st.session_state.get("role")
    ui.inject_css(sidebar_visible=bool(role))

    if not role:
        render_login()
        return

    st.session_state.setdefault("nav_key", "overview")
    items = nav_items_for_role(role)
    keys = [x[0] for x in items]
    labels = [x[1] for x in items]
    if st.session_state["nav_key"] not in keys:
        st.session_state["nav_key"] = keys[0]

    try:
        radio_index = keys.index(st.session_state["nav_key"])
    except ValueError:
        radio_index = 0

    with st.sidebar:
        ui.sidebar_brand()
        ui.sidebar_user_block(role)
        sel_label = st.radio(
            "Navigation",
            labels,
            index=radio_index,
            label_visibility="collapsed",
        )
        st.session_state["nav_key"] = keys[labels.index(sel_label)]
        st.divider()
        if st.button("Sign out", use_container_width=True):
            st.session_state.pop("role", None)
            st.session_state.pop("nav_key", None)
            st.rerun()

    fn = dict((k, f) for k, _, f in items)[st.session_state["nav_key"]]
    fn()


if __name__ == "__main__":
    main()
