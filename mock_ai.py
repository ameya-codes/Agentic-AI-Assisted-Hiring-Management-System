"""
Mock AI helpers for the Hiring Management POC.
If OPENAI_API_KEY is set, some functions call OpenAI first (see llm.py); otherwise outputs are local heuristics.
"""

import re
from typing import Any

import llm
import prompts as pr


def _word_set(text: str) -> set[str]:
    words = re.findall(r"[A-Za-z0-9+#.]+", (text or "").lower())
    return set(words)


KNOWN_SKILLS = {
    "python",
    "java",
    "javascript",
    "typescript",
    "react",
    "node",
    "sql",
    "postgresql",
    "mysql",
    "aws",
    "gcp",
    "azure",
    "kubernetes",
    "docker",
    "fastapi",
    "django",
    "flask",
    "pandas",
    "spark",
    "tableau",
    "looker",
    "excel",
    "ml",
    "ai",
    "nlp",
    "c++",
    "go",
    "rust",
    "graphql",
    "rest",
    "api",
    "terraform",
    "linux",
    "git",
}


def generate_job_description(
    title: str,
    department: str,
    location: str,
    salary_min: float,
    salary_max: float,
    experience_level: str,
    required_skills: str,
    notes: str = "",
) -> dict[str, str]:
    """Return structured AI output for job requisition drafting (OpenAI if configured, else local)."""
    data = llm.openai_chat_json(
        pr.JOB_DESCRIPTION_SYSTEM,
        pr.job_description_user(
            title, department, location, salary_min, salary_max, experience_level, required_skills, notes
        ),
    )
    if data and all(
        k in data and isinstance(data[k], str)
        for k in ("description", "recommended_skills", "bias_check", "improvements")
    ):
        return {
            "description": str(data["description"]).strip(),
            "recommended_skills": str(data["recommended_skills"]).strip(),
            "bias_check": str(data["bias_check"]).strip(),
            "improvements": str(data["improvements"]).strip(),
        }

    skills_list = [s.strip() for s in (required_skills or "").split(",") if s.strip()]
    skills_bullets = "\n".join(f"- {s}" for s in skills_list[:12]) or "- Strong problem solving and collaboration"
    band = f"${salary_min:,.0f} – ${salary_max:,.0f}" if salary_min and salary_max else "Competitive"

    description = f"""## {title}

**Department:** {department}  
**Location:** {location}  
**Experience:** {experience_level}  
**Compensation band (indicative):** {band}

### Role overview
We are looking for a {experience_level.lower()}-level {title} to join {department} and help deliver reliable, user-centered outcomes. You will partner with stakeholders across the company, contribute to design discussions, and ship high-quality work in a collaborative environment.

### What you will do
- Own meaningful slices of product or platform delivery end-to-end.
- Collaborate with peers to clarify requirements, estimate work, and improve team practices.
- Participate in code/design reviews and help raise the quality bar.
- Communicate progress and risks clearly to partners and leadership.

### Required qualifications
{skills_bullets}

### Nice to have
- Experience in regulated or enterprise environments.
- Comfort with observability, testing strategy, and incremental delivery.

### Why join us
You will work on problems that matter, with supportive teammates and clear expectations. {notes[:200] if notes else ''}
""".strip()

    extra_skills = []
    for s in ["Stakeholder communication", "Documentation", "Agile delivery", "Data-informed decisions"]:
        if s.lower() not in " ".join(skills_list).lower():
            extra_skills.append(s)

    bias_note = (
        "Bias check: Role text uses neutral titles and avoids gendered or age-biased language. "
        "Ensure interview panels are diverse and criteria map directly to job requirements."
    )

    improvements = (
        "- Tie required skills to measurable outcomes (e.g., 'ship X in Y weeks').\n"
        "- Clarify remote/hybrid expectations and core working hours.\n"
        "- Add 2–3 concrete success metrics for the first 90 days.\n"
        "- Confirm leveling aligns with internal career ladders."
    )

    return {
        "description": description,
        "recommended_skills": ", ".join(extra_skills[:4]),
        "bias_check": bias_note,
        "improvements": improvements,
    }


def screen_resume(resume_text: str, job_skills: str, job_title: str) -> dict[str, Any]:
    """Resume screening: OpenAI if configured, else local heuristics."""
    data = llm.openai_chat_json(
        pr.RESUME_SCREEN_SYSTEM,
        pr.resume_screen_user(job_title, job_skills, resume_text or ""),
    )
    req = ("skills", "experience", "education", "certifications", "strengths", "weaknesses", "match_score", "recommendation")
    if data and all(k in data for k in req):
        try:
            score = int(data["match_score"])
        except (TypeError, ValueError):
            score = None
        rec = str(data.get("recommendation", "")).strip()
        if score is not None and rec in ("Reject", "Hold", "Proceed to Interview"):
            score = max(0, min(100, score))
            return {
                "skills": str(data["skills"]),
                "experience": str(data["experience"]),
                "education": str(data["education"]),
                "certifications": str(data["certifications"]),
                "strengths": str(data["strengths"]),
                "weaknesses": str(data["weaknesses"]),
                "match_score": score,
                "recommendation": rec,
            }

    text = resume_text or ""
    words = _word_set(text)
    job_words = _word_set(job_skills + " " + job_title)

    matched = sorted(KNOWN_SKILLS.intersection(words))
    overlap = sorted(KNOWN_SKILLS.intersection(job_words))
    matched_for_job = [m for m in matched if m in overlap] or matched[:6]

    years = re.findall(r"(\d+)\+?\s*years?", text.lower())
    exp_years = int(years[0]) if years else min(12, max(1, len(text) // 800))

    edu = "Not specified in resume text"
    if "bachelor" in text.lower() or " bs " in text.lower() or "b.s." in text.lower():
        edu = "Bachelor's degree (inferred from resume)"
    if "master" in text.lower() or " ms " in text.lower():
        edu = "Master's degree (inferred from resume)"

    certs = []
    for c in ["AWS", "GCP", "Azure", "PMP", "Scrum", "Kubernetes"]:
        if c.lower() in text.lower():
            certs.append(c)
    cert_str = ", ".join(certs) if certs else "None listed (add certifications if applicable)"

    score = 45
    score += min(25, 3 * len(matched_for_job))
    score += min(15, len(text) // 400)
    if overlap and matched_for_job:
        score += min(15, 5 * len(set(matched_for_job).intersection(overlap)))
    score = int(max(0, min(100, score)))

    strengths = []
    if matched_for_job:
        strengths.append(f"Aligned technical signals: {', '.join(matched_for_job[:6])}")
    if len(text) > 600:
        strengths.append("Resume provides enough detail to assess scope and impact.")
    if not strengths:
        strengths.append("Shows interest in the role domain; room to probe in interview.")

    weaknesses = []
    if len(matched_for_job) < 2:
        weaknesses.append("Limited explicit overlap with stated job skills—validate depth in screening.")
    if len(text) < 350:
        weaknesses.append("Resume is short on quantified outcomes (metrics, scale, timelines).")
    if not weaknesses:
        weaknesses.append("Minor gaps only; confirm seniority expectations with hiring manager.")

    if score >= 78:
        rec = "Proceed to Interview"
    elif score >= 58:
        rec = "Hold"
    else:
        rec = "Reject"

    return {
        "skills": ", ".join(matched[:10]) if matched else "General professional skills (extract manually if needed)",
        "experience": f"Estimated relevant experience signal: ~{exp_years}+ years (heuristic from resume length/keywords).",
        "education": edu,
        "certifications": cert_str,
        "strengths": "; ".join(strengths),
        "weaknesses": "; ".join(weaknesses),
        "match_score": score,
        "recommendation": rec,
    }


def rank_candidates(rows: list[dict]) -> list[dict]:
    """Sort by match_score descending; attach rank index."""
    sorted_rows = sorted(rows, key=lambda r: r.get("match_score") or 0, reverse=True)
    out = []
    for i, r in enumerate(sorted_rows, start=1):
        item = dict(r)
        item["rank"] = i
        out.append(item)
    return out


def generate_interview_email(
    candidate_name: str,
    job_title: str,
    interviewer_name: str,
    when: str,
    interview_type: str,
) -> str:
    body = llm.openai_chat_text(
        pr.INTERVIEW_EMAIL_SYSTEM,
        pr.interview_email_user(candidate_name, job_title, interviewer_name, when, interview_type),
    )
    if body:
        return body.strip()
    return f"""Subject: Interview invitation — {job_title} role

Hi {candidate_name},

Thank you for your interest in the {job_title} position. We would like to schedule your {interview_type.lower()} interview with {interviewer_name}.

**Proposed time:** {when}  
**Format:** Video call (link to be shared separately)

Please reply to confirm availability. If you need accommodations or an alternate time window, let us know and we will do our best to accommodate.

Best regards,  
HireFlow AI — Talent team
"""


def generate_interview_questions(job_title: str, interview_type: str, resume_snippet: str = "") -> dict[str, str]:
    data = llm.openai_chat_json(
        pr.INTERVIEW_QUESTIONS_SYSTEM,
        pr.interview_questions_user(job_title, interview_type, resume_snippet),
    )
    if data and isinstance(data.get("technical"), str) and isinstance(data.get("behavioral"), str):
        return {
            "technical": str(data["technical"]).strip(),
            "behavioral": str(data["behavioral"]).strip(),
        }
    snippet = (resume_snippet or "")[:400]
    tech = (
        f"Given the {job_title} role, probe system design tradeoffs for a core workflow you would own.\n"
        "- Walk through a recent project where you improved reliability or performance—what metrics moved?\n"
        "- How do you approach testing and rollout risk for a change touching production data?\n"
        f"- Context note from resume excerpt: {snippet[:200]}..."
    )
    behavioral = (
        "- Tell me about a time you disagreed with a stakeholder—how did you resolve it?\n"
        "- Describe a situation with ambiguous requirements. How did you drive clarity?\n"
        "- Share an example of mentoring or uplifting a teammate.\n"
    )
    if interview_type.lower() == "behavioral":
        tech = "Keep technical depth light; focus on collaboration examples tied to the role."
    if interview_type.lower() == "final":
        behavioral += "- What are you looking for in your next team and manager?\n"
    return {"technical": tech.strip(), "behavioral": behavioral.strip()}


def summarize_feedback(
    technical: str,
    communication: str,
    rating: int,
    hire_decision: str,
) -> dict[str, str]:
    data = llm.openai_chat_json(
        pr.FEEDBACK_SUMMARY_SYSTEM,
        pr.feedback_summary_user(technical, communication, rating, hire_decision),
    )
    keys = ("summary", "sentiment", "strengths", "risks", "final_recommendation")
    if data and all(isinstance(data.get(k), str) for k in keys):
        sent = str(data["sentiment"]).strip()
        if sent in ("Positive", "Neutral", "Negative"):
            return {k: str(data[k]).strip() for k in keys}  # type: ignore[misc]

    tone = "positive" if rating >= 4 else "mixed" if rating == 3 else "concerning"
    sentiment = "Positive" if rating >= 4 else "Neutral" if rating == 3 else "Negative"

    summary = (
        f"Overall signal is {tone} (self-reported rating {rating}/5). "
        f"Technical notes emphasize: {(technical or '')[:220]}. "
        f"Communication notes emphasize: {(communication or '')[:220]}."
    )

    strengths = []
    if "clear" in (communication or "").lower() or rating >= 4:
        strengths.append("Clear communication and structured thinking (based on interviewer notes).")
    if len((technical or "")) > 40:
        strengths.append("Demonstrated relevant technical depth in discussed scenarios.")
    if not strengths:
        strengths.append("Shows potential in areas aligned to role; confirm with follow-up where needed.")

    risks = []
    if rating <= 3:
        risks.append("Rating suggests gaps versus bar—align on must-have competencies.")
    if "weak" in (technical or "").lower() or "concern" in (technical or "").lower():
        risks.append("Technical concerns flagged—validate with a second interviewer if proceeding.")
    if hire_decision == "No Hire":
        risks.append("Interviewer leaning no-hire; human panel should confirm before closing candidate.")
    if not risks:
        risks.append("No major red flags surfaced in submitted notes (still verify references and work samples).")

    final_rec = (
        "Proceed toward offer discussion (pending approvals)"
        if hire_decision == "Hire"
        else "Additional interview recommended"
        if hire_decision == "Maybe"
        else "Do not proceed unless hiring manager overrides with documented rationale"
    )

    return {
        "summary": summary.strip(),
        "sentiment": sentiment,
        "strengths": " ".join(strengths),
        "risks": " ".join(risks),
        "final_recommendation": final_rec,
    }


def generate_offer_letter(
    candidate_name: str,
    job_title: str,
    salary: float,
    start_date: str,
    reporting_manager: str,
) -> str:
    body = llm.openai_chat_text(
        pr.OFFER_LETTER_SYSTEM,
        pr.offer_letter_user(candidate_name, job_title, salary, start_date, reporting_manager),
    )
    if body:
        return body.strip()
    return f"""
OFFER OF EMPLOYMENT (DRAFT — FOR INTERNAL REVIEW)

Date: {start_date}

Dear {candidate_name},

On behalf of the company, we are pleased to offer you the position of **{job_title}**, reporting to **{reporting_manager}**.

**Compensation:** Base salary of ${salary:,.2f} per year, subject to payroll deductions and company policies.  
**Start date:** {start_date}

This offer is contingent upon successful completion of pre-employment requirements, including background verification and proof of eligibility to work.

This letter is a demonstration artifact for a class project and is not legally binding.

Sincerely,  
Human Resources
""".strip()


def onboarding_chatbot_response(question: str) -> str:
    ans = llm.openai_chat_text(
        pr.ONBOARDING_ASSISTANT_SYSTEM,
        f"Employee question:\n{question.strip()[:2000]}",
    )
    if ans:
        return ans.strip()
    q = (question or "").lower()
    if "laptop" in q or "it" in q or "equipment" in q:
        return (
            "IT typically ships hardware after your start date is confirmed. "
            "You will receive tracking details by email. If you need software installed early, ask your recruiter to open an IT ticket."
        )
    if "background" in q or "verification" in q:
        return (
            "Background verification is handled by a third-party vendor. Timeline is often 3–10 business days. "
            "Respond promptly to any requests for additional information."
        )
    if "orientation" in q or "hr" in q:
        return (
            "HR orientation covers policies, benefits enrollment, and payroll setup. "
            "You will get a calendar invite with the video link and pre-read materials."
        )
    if "id" in q or "document" in q or "i-9" in q:
        return (
            "You will be asked to upload government ID and work authorization documents through the secure onboarding portal. "
            "Use the exact legal name that should appear on payroll records."
        )
    return (
        "Thanks for your question. In a real system, this assistant would pull answers from your company handbook and ticketing policies. "
        "For this POC: contact your recruiter for role-specific logistics and HR for policy questions."
    )
