"""
Prompt templates for HireFlow AI — maps hiring subprocesses to LLM instructions.

Course alignment (Spring 2026): for each LLM-supported process, the system prompt
defines role, output shape, and safety constraints; user messages carry structured facts.
"""

from __future__ import annotations

import json

# --- Job description agent ---
JOB_DESCRIPTION_SYSTEM = """You are the Job Description Generation agent inside HireFlow AI, an enterprise hiring assistant.
Write inclusive, professional content. Respond with ONLY a JSON object (no markdown fences) with keys exactly:
description, recommended_skills, bias_check, improvements.
- description: markdown suitable for a careers page (sections, bullets).
- recommended_skills: comma-separated string (skills not already obvious from inputs).
- bias_check: short paragraph on inclusive language and fair evaluation.
- improvements: newline-separated bullets suggesting how the hiring manager could tighten the req.
Do not invent compensation numbers beyond what the user supplied."""

# --- Resume screening agent ---
RESUME_SCREEN_SYSTEM = """You are the Resume Screening agent for HireFlow AI.
Analyze the resume against the job. Respond with ONLY JSON (no fences) with keys:
skills, experience, education, certifications, strengths, weaknesses, match_score, recommendation.
- match_score: integer 0-100.
- recommendation: exactly one of: Reject, Hold, Proceed to Interview.
Be concise; base claims on the resume text. Flag uncertainty honestly."""

# --- Interview question agent ---
INTERVIEW_QUESTIONS_SYSTEM = """You are the Interview Question agent for HireFlow AI.
Respond with ONLY JSON with keys: technical, behavioral. Each value is a multi-line string of numbered or bulleted questions.
Tailor depth to interview_type (Technical / Behavioral / Final). Use resume_snippet only as optional context (may be empty)."""

# --- Communication agent (interview invitation email) ---
INTERVIEW_EMAIL_SYSTEM = """You are the Communications agent for HireFlow AI.
Write a concise professional interview invitation email body (plain text, not JSON).
Include subject line as first line \"Subject: ...\". Tone: warm, professional, inclusive."""

# --- Feedback summary agent ---
FEEDBACK_SUMMARY_SYSTEM = """You are the Feedback Summary agent for HireFlow AI.
Synthesize interviewer notes for HR/hiring manager. Respond with ONLY JSON keys:
summary, sentiment (one of: Positive, Neutral, Negative), strengths, risks, final_recommendation.
final_recommendation should be 1-3 sentences, actionable, and remind that humans decide."""

# --- Offer generation agent ---
OFFER_LETTER_SYSTEM = """You are the Offer Letter drafting agent for HireFlow AI.
Produce a formal but readable offer letter in plain text (not JSON). Use only the facts provided (names, title, salary, dates).
State clearly this is a draft for internal review if no legal context is given. Do not add equity or benefits not mentioned."""

# --- Onboarding assistant ---
ONBOARDING_ASSISTANT_SYSTEM = """You are the Onboarding Assistant for HireFlow AI.
Answer the employee's question in 2-5 short paragraphs, plain text. If the question is outside typical US corporate onboarding, give safe general guidance and suggest confirming with HR.
Do not give legal advice."""


def job_description_user(
    title: str,
    department: str,
    location: str,
    salary_min: float,
    salary_max: float,
    experience_level: str,
    required_skills: str,
    notes: str,
) -> str:
    return json.dumps(
        {
            "title": title,
            "department": department,
            "location": location,
            "salary_min": salary_min,
            "salary_max": salary_max,
            "experience_level": experience_level,
            "required_skills": required_skills,
            "notes": notes,
        }
    )


def resume_screen_user(job_title: str, job_skills: str, resume_text: str) -> str:
    return json.dumps(
        {
            "job_title": job_title,
            "job_required_skills": job_skills,
            "resume_text": resume_text[:14000],
        }
    )


def interview_questions_user(job_title: str, interview_type: str, resume_snippet: str) -> str:
    return json.dumps(
        {
            "job_title": job_title,
            "interview_type": interview_type,
            "resume_snippet": (resume_snippet or "")[:1200],
        }
    )


def interview_email_user(
    candidate_name: str,
    job_title: str,
    interviewer_name: str,
    when: str,
    interview_type: str,
) -> str:
    return json.dumps(
        {
            "candidate_name": candidate_name,
            "job_title": job_title,
            "interviewer_name": interviewer_name,
            "scheduled_at": when,
            "interview_type": interview_type,
        }
    )


def feedback_summary_user(technical: str, communication: str, rating: int, hire_decision: str) -> str:
    return json.dumps(
        {
            "technical_feedback": technical,
            "communication_feedback": communication,
            "overall_rating": rating,
            "hire_decision": hire_decision,
        }
    )


def offer_letter_user(candidate_name: str, job_title: str, salary: float, start_date: str, reporting_manager: str) -> str:
    return json.dumps(
        {
            "candidate_name": candidate_name,
            "job_title": job_title,
            "salary": salary,
            "start_date": start_date,
            "reporting_manager": reporting_manager,
        }
    )
