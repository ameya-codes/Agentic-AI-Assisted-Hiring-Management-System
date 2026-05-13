#!/usr/bin/env python3
"""
Walk through the README demo flow using the same DB + mock_ai as the Streamlit app.
Run from project root:  .venv/bin/python demo_flow_e2e.py
"""

import db
import mock_ai


def main() -> None:
    db.init_db()
    db.seed_if_empty()

    print("1) Login / Role — (UI only; script runs as backend walkthrough)\n")

    print("2) Job Requisition — AI draft + save")
    ai_job = mock_ai.generate_job_description(
        title="Security Engineer II",
        department="Security",
        location="Remote",
        salary_min=130000,
        salary_max=160000,
        experience_level="Mid",
        required_skills="Python, AWS, threat modeling, IAM",
        notes="Focus on secure SDLC.",
    )
    jid = db.insert_job(
        {
            "title": "Security Engineer II",
            "department": "Security",
            "location": "Remote",
            "salary_min": 130000.0,
            "salary_max": 160000.0,
            "experience_level": "Mid",
            "required_skills": "Python, AWS, threat modeling, IAM",
            "description": ai_job["description"][:2000],
        }
    )
    db.log_audit("DEMO", "jobs", jid, "HR Recruiter", "E2E: job created")
    print(f"   Saved job id={jid}; bias note snippet: {ai_job['bias_check'][:60]}...\n")

    print("3) Resume Screening — mock screen + save candidate")
    resume = """
    Taylor Nguyen — Security Engineer with 6 years experience.
    Skills: Python, AWS, Kubernetes, Terraform, threat modeling, IAM, SOC2 audits.
    BS Computer Science. AWS Security Specialty. Led zero-trust rollout for SaaS product.
    """
    screening = mock_ai.screen_resume(resume, "Python, AWS, threat modeling, IAM", "Security Engineer II")
    cid = db.insert_candidate_screening(
        jid,
        "Taylor Nguyen",
        "taylor.nguyen@example.com",
        resume.strip(),
        screening,
    )
    db.log_audit("DEMO", "candidates", cid, "HR Recruiter", "E2E: screening saved")
    print(f"   Candidate id={cid}, match={screening['match_score']}, rec={screening['recommendation']}\n")

    print("4) Candidate Ranking — shortlist (human step)")
    db.update_candidate_status(cid, "Shortlisted")
    db.log_audit("DEMO", "candidates", cid, "Hiring Manager", "E2E: shortlisted")
    print(f"   Status -> Shortlisted\n")

    print("5) Interview Scheduling — invitation + questions + save")
    when = "2026-06-01 15:00"
    interviewer = "Riley Chen"
    itype = "Technical"
    email = mock_ai.generate_interview_email(
        "Taylor Nguyen", "Security Engineer II", interviewer, when, itype
    )
    qs = mock_ai.generate_interview_questions("Security Engineer II", itype, resume[:500])
    iid = db.insert_interview(
        {
            "candidate_id": cid,
            "interviewer_name": interviewer,
            "scheduled_at": when,
            "interview_type": itype,
            "invitation_email": email,
            "tech_questions": qs["technical"],
            "behavioral_questions": qs["behavioral"],
        }
    )
    db.update_candidate_status(cid, "Interview Scheduled")
    db.log_audit("DEMO", "interviews", iid, "Hiring Manager", "E2E: interview scheduled")
    print(f"   Interview id={iid}\n")

    print("6) Interview Feedback — AI summary + save")
    tech = "Strong threat modeling and AWS controls discussion."
    comm = "Clear, structured answers."
    rating = 5
    decision = "Hire"
    fb_ai = mock_ai.summarize_feedback(tech, comm, rating, decision)
    fid = db.insert_feedback(
        {
            "interview_id": iid,
            "technical_feedback": tech,
            "communication_feedback": comm,
            "overall_rating": rating,
            "hire_decision": decision,
            "ai_summary": fb_ai["summary"],
            "sentiment": fb_ai["sentiment"],
            "candidate_strengths": fb_ai["strengths"],
            "candidate_risks": fb_ai["risks"],
            "final_recommendation": fb_ai["final_recommendation"],
        }
    )
    db.update_candidate_status(cid, "Interview Completed")
    db.log_audit("DEMO", "feedback", fid, "Interviewer", "E2E: feedback saved")
    print(f"   Feedback id={fid}; sentiment={fb_ai['sentiment']}\n")

    print("7) Offer Letter — draft + HR approval")
    salary = 142500.0
    start = "2026-07-07"
    letter = mock_ai.generate_offer_letter(
        "Taylor Nguyen", "Security Engineer II", salary, start, "Morgan Singh (Security Lead)"
    )
    oid = db.insert_offer(
        {
            "candidate_id": cid,
            "salary": salary,
            "start_date": start,
            "job_title": "Security Engineer II",
            "reporting_manager": "Morgan Singh (Security Lead)",
            "letter_text": letter,
            "approval_status": "Draft",
        }
    )
    db.update_candidate_status(cid, "Offer Generated")
    db.update_offer_status(oid, "Approved")
    db.log_audit("DEMO", "offers", oid, "HR Recruiter", "E2E: offer approved")
    print(f"   Offer id={oid}, status=Approved, salary=${salary:,.0f}\n")

    print("8) Onboarding — checklist + FAQ")
    tasks = db.get_onboarding_tasks(cid)
    print(f"   {len(tasks)} onboarding task(s) for candidate {cid}")
    faq = mock_ai.onboarding_chatbot_response("When will I receive my laptop?")
    print(f"   FAQ sample: {faq[:120]}...\n")

    print("9) AI Agents Overview — see app page (static content in app.py)\n")
    print("Done. Open Streamlit and confirm: new job, Taylor Nguyen in ranking, pipeline updates.")


if __name__ == "__main__":
    main()
