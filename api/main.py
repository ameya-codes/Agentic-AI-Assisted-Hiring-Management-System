"""
FastAPI backend for the React hiring UI.
Run from project root:  uvicorn api.main:app --reload --port 8000
"""

from __future__ import annotations

from contextlib import asynccontextmanager
import os
from pathlib import Path
import sys
from typing import Annotated

# Project root on path so `import db` / `import mock_ai` work
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

try:
    from dotenv import load_dotenv

    load_dotenv(ROOT / ".env")
except ImportError:
    pass

from fastapi import Depends, FastAPI, File, Form, Header, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

import db
import mock_ai
import resume_extract

DEMO_ROLES = frozenset(
    {"Hiring Manager", "HR Recruiter", "Candidate", "Interviewer"}
)


@asynccontextmanager
async def lifespan(_: FastAPI):
    db.init_db()
    db.seed_if_empty()
    yield


app = FastAPI(title="HireFlow AI API", lifespan=lifespan)

_cors_origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:5174",
    "http://127.0.0.1:5174",
]
_extra = os.getenv("CORS_EXTRA_ORIGINS", "").strip()
if _extra:
    _cors_origins.extend([o.strip() for o in _extra.split(",") if o.strip()])

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    # Preview + production Vite sites on Vercel (*.vercel.app)
    allow_origin_regex=r"https://.*\.vercel\.app$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def role_hdr(x_demo_role: str | None) -> str:
    if not x_demo_role or x_demo_role not in DEMO_ROLES:
        return "Anonymous"
    return x_demo_role


def _require_internal_role(x_demo_role: str | None = Header(default=None)) -> str:
    r = role_hdr(x_demo_role)
    if r == "Candidate":
        raise HTTPException(
            status_code=403,
            detail="This hiring workspace data is not available on the candidate careers view.",
        )
    return r


def _require_candidate_role(x_demo_role: str | None = Header(default=None)) -> str:
    r = role_hdr(x_demo_role)
    if r != "Candidate":
        raise HTTPException(
            status_code=403,
            detail="Sign in with the Candidate demo profile to use the careers portal.",
        )
    return r


InternalRole = Annotated[str, Depends(_require_internal_role)]
CandidateRole = Annotated[str, Depends(_require_candidate_role)]

MAX_RESUME_BYTES = 5 * 1024 * 1024


# --- Pydantic ---


class JobCreate(BaseModel):
    title: str
    department: str = ""
    location: str = ""
    salary_min: float = 0
    salary_max: float = 0
    experience_level: str = "Mid"
    required_skills: str = ""
    description: str = ""


class JobDescriptionAIRequest(BaseModel):
    title: str
    department: str = ""
    location: str = ""
    salary_min: float = 0
    salary_max: float = 0
    experience_level: str = "Mid"
    required_skills: str = ""
    notes: str = ""


class PreviewScreenRequest(BaseModel):
    job_id: int
    resume_text: str


class ScreenCandidateRequest(BaseModel):
    job_id: int
    name: str
    email: str = ""
    resume_text: str


class StatusUpdate(BaseModel):
    status: str


class ScheduleInterviewRequest(BaseModel):
    candidate_id: int
    interviewer_name: str
    scheduled_at: str
    interview_type: str = "Technical"


class FeedbackCreate(BaseModel):
    interview_id: int
    technical_feedback: str = ""
    communication_feedback: str = ""
    overall_rating: int = Field(ge=1, le=5)
    hire_decision: str = "Maybe"


class OfferCreate(BaseModel):
    candidate_id: int
    salary: float
    start_date: str
    job_title: str
    reporting_manager: str = ""


class OfferStatusUpdate(BaseModel):
    approval_status: str


class OnboardingTaskUpdate(BaseModel):
    completed: bool


def _row_to_dict(row) -> dict:
    return {k: row[k] for k in row.keys()}


# --- Routes ---


@app.get("/api/health")
def health():
    return {"ok": True}


@app.get("/api/careers/open-roles")
def api_careers_open_roles(_role: CandidateRole):
    rows = db.list_open_jobs_public()
    return [_row_to_dict(r) for r in rows]


@app.get("/api/careers/overview")
def api_careers_overview(_role: CandidateRole, email: str = ""):
    s = db.dashboard_stats()
    apps = db.applications_for_email(email)
    return {
        "open_roles": s["open_jobs"],
        "applications": [_row_to_dict(r) for r in apps],
    }


@app.get("/api/careers/my-applications")
def api_careers_my_applications(_role: CandidateRole, email: str = ""):
    rows = db.applications_for_email(email)
    return [_row_to_dict(r) for r in rows]


@app.post("/api/careers/apply")
async def api_careers_apply(
    _role: CandidateRole,
    job_id: int = Form(),
    name: str = Form(),
    email: str = Form(),
    resume: UploadFile = File(),
):
    raw = await resume.read()
    if len(raw) > MAX_RESUME_BYTES:
        raise HTTPException(status_code=413, detail="Resume must be 5MB or smaller.")
    fn = resume.filename or "resume.pdf"
    try:
        text = resume_extract.extract_resume_text(fn, raw)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    if len(text.strip()) < 40:
        raise HTTPException(
            status_code=400,
            detail="Could not read enough text from the resume. Try another PDF or DOCX export.",
        )
    with db.get_conn() as conn:
        row = conn.execute(
            "SELECT id, title, required_skills, status FROM jobs WHERE id = ?",
            (job_id,),
        ).fetchone()
    if not row or row["status"] != "Open":
        raise HTTPException(status_code=404, detail="This role is not open for applications.")
    job = _row_to_dict(row)
    screening = mock_ai.screen_resume(
        text,
        job.get("required_skills") or "",
        job.get("title") or "",
    )
    cid = db.insert_candidate_screening(
        job_id,
        name.strip(),
        email.strip(),
        text,
        screening,
    )
    db.log_audit(
        "CAREER_APPLY",
        "candidates",
        cid,
        "Candidate",
        f"{name.strip()} → {job.get('title')}",
    )
    return {"candidate_id": cid, "job_title": job.get("title"), "screening": screening}


@app.get("/api/dashboard")
def api_dashboard(_role: InternalRole, job_id: int | None = None):
    s = db.dashboard_stats(job_id)
    pipe = [{"status": r["status"], "count": r["cnt"]} for r in s["pipeline"]]
    req_rows = db.list_jobs_with_applicant_counts(job_id)
    requisitions = [_row_to_dict(r) for r in req_rows]
    headline = None
    if job_id is not None:
        with db.get_conn() as conn:
            r = conn.execute(
                "SELECT id, title, department, location, status FROM jobs WHERE id = ?",
                (job_id,),
            ).fetchone()
        headline = _row_to_dict(r) if r else None
    return {
        "open_jobs": s["open_jobs"],
        "total_candidates": s["total_candidates"],
        "shortlisted": s["shortlisted"],
        "interviews": s["interviews"],
        "offers": s["offers"],
        "pipeline": pipe,
        "requisitions": requisitions,
        "active_requisition": headline,
    }


@app.get("/api/jobs/applicants")
def api_job_applicants(_role: InternalRole, job_id: int | None = None):
    rows = db.list_applicants_for_staff(job_id)
    return [_row_to_dict(r) for r in rows]


@app.get("/api/jobs")
def api_jobs(_role: InternalRole):
    rows = db.list_jobs()
    return [_row_to_dict(r) for r in rows]


@app.post("/api/jobs")
def api_create_job(body: JobCreate, role: InternalRole):
    jid = db.insert_job(body.model_dump())
    db.log_audit("CREATE_JOB", "jobs", jid, role, body.title)
    return {"id": jid}


@app.post("/api/ai/job-description")
def api_ai_job_description(body: JobDescriptionAIRequest, _role: InternalRole):
    return mock_ai.generate_job_description(
        body.title,
        body.department,
        body.location,
        body.salary_min,
        body.salary_max,
        body.experience_level,
        body.required_skills,
        notes=body.notes,
    )


@app.get("/api/candidates/ranked")
def api_ranked(_role: InternalRole, job_id: int | None = None):
    rows = db.ranked_candidates(job_id)
    base = [_row_to_dict(r) for r in rows]
    return mock_ai.rank_candidates(base)


@app.patch("/api/candidates/{candidate_id}/status")
def api_candidate_status(
    candidate_id: int,
    body: StatusUpdate,
    role: InternalRole,
):
    db.update_candidate_status(candidate_id, body.status)
    db.log_audit(
        "STATUS_CHANGE",
        "candidates",
        candidate_id,
        role,
        body.status,
    )
    return {"ok": True}


@app.get("/api/candidates/shortlisted")
def api_shortlisted(_role: InternalRole, job_id: int | None = None):
    rows = db.shortlisted_candidates(job_id)
    return [_row_to_dict(r) for r in rows]


@app.post("/api/ai/preview-screen")
def api_preview_screen(body: PreviewScreenRequest, _role: InternalRole):
    with db.get_conn() as conn:
        job = conn.execute("SELECT * FROM jobs WHERE id = ?", (body.job_id,)).fetchone()
    if not job:
        raise HTTPException(404, "Job not found")
    job = _row_to_dict(job)
    return mock_ai.screen_resume(
        body.resume_text,
        job.get("required_skills") or "",
        job.get("title") or "",
    )


@app.post("/api/candidates/screen")
def api_screen_candidate(
    body: ScreenCandidateRequest,
    role: InternalRole,
):
    with db.get_conn() as conn:
        job = conn.execute("SELECT * FROM jobs WHERE id = ?", (body.job_id,)).fetchone()
    if not job:
        raise HTTPException(404, "Job not found")
    job = _row_to_dict(job)
    screening = mock_ai.screen_resume(
        body.resume_text,
        job.get("required_skills") or "",
        job.get("title") or "",
    )
    cid = db.insert_candidate_screening(
        body.job_id,
        body.name,
        body.email,
        body.resume_text,
        screening,
    )
    db.log_audit(
        "SCREEN_RESUME",
        "candidates",
        cid,
        role,
        body.name,
    )
    return {"candidate_id": cid, "screening": screening}


@app.post("/api/interviews")
def api_schedule_interview(
    body: ScheduleInterviewRequest,
    role: InternalRole,
):
    with db.get_conn() as conn:
        c = conn.execute(
            "SELECT c.name, j.title FROM candidates c JOIN jobs j ON j.id = c.job_id WHERE c.id = ?",
            (body.candidate_id,),
        ).fetchone()
        resume_row = conn.execute(
            "SELECT resume_text FROM candidates WHERE id = ?",
            (body.candidate_id,),
        ).fetchone()
    if not c:
        raise HTTPException(404, "Candidate not found")
    name, title = c["name"], c["title"]
    resume_snippet = (resume_row["resume_text"] or "") if resume_row else ""
    email = mock_ai.generate_interview_email(
        name, title, body.interviewer_name, body.scheduled_at, body.interview_type
    )
    qs = mock_ai.generate_interview_questions(title, body.interview_type, resume_snippet)
    iid = db.insert_interview(
        {
            "candidate_id": body.candidate_id,
            "interviewer_name": body.interviewer_name,
            "scheduled_at": body.scheduled_at,
            "interview_type": body.interview_type,
            "invitation_email": email,
            "tech_questions": qs["technical"],
            "behavioral_questions": qs["behavioral"],
        }
    )
    db.update_candidate_status(body.candidate_id, "Interview Scheduled")
    db.log_audit("SCHEDULE_INTERVIEW", "interviews", iid, role, str(body.candidate_id))
    return {"id": iid, "invitation_email": email, "questions": qs}


@app.get("/api/interviews")
def api_list_interviews(_role: InternalRole, job_id: int | None = None):
    rows = db.list_interviews_for_feedback(job_id)
    return [_row_to_dict(r) for r in rows]


@app.post("/api/feedback")
def api_feedback(body: FeedbackCreate, role: InternalRole):
    out = mock_ai.summarize_feedback(
        body.technical_feedback,
        body.communication_feedback,
        body.overall_rating,
        body.hire_decision,
    )
    fid = db.insert_feedback(
        {
            "interview_id": body.interview_id,
            "technical_feedback": body.technical_feedback,
            "communication_feedback": body.communication_feedback,
            "overall_rating": body.overall_rating,
            "hire_decision": body.hire_decision,
            "ai_summary": out["summary"],
            "sentiment": out["sentiment"],
            "candidate_strengths": out["strengths"],
            "candidate_risks": out["risks"],
            "final_recommendation": out["final_recommendation"],
        }
    )
    with db.get_conn() as conn:
        row = conn.execute(
            "SELECT candidate_id FROM interviews WHERE id = ?",
            (body.interview_id,),
        ).fetchone()
    if row:
        db.update_candidate_status(row["candidate_id"], "Interview Completed")
    db.log_audit("FEEDBACK", "feedback", fid, role, f"interview {body.interview_id}")
    return {"id": fid, "ai": out}


@app.get("/api/offers/eligible-candidates")
def api_offer_pool(_role: InternalRole, job_id: int | None = None):
    rows = db.candidates_for_offer(job_id)
    return [_row_to_dict(r) for r in rows]


@app.get("/api/offers")
def api_offers(_role: InternalRole, job_id: int | None = None):
    rows = db.list_offers(job_id)
    return [_row_to_dict(r) for r in rows]


@app.post("/api/offers")
def api_create_offer(body: OfferCreate, role: InternalRole):
    with db.get_conn() as conn:
        nm = conn.execute("SELECT name FROM candidates WHERE id = ?", (body.candidate_id,)).fetchone()
    name = nm["name"] if nm else "Candidate"
    letter = mock_ai.generate_offer_letter(
        name, body.job_title, body.salary, body.start_date, body.reporting_manager
    )
    oid = db.insert_offer(
        {
            "candidate_id": body.candidate_id,
            "salary": body.salary,
            "start_date": body.start_date,
            "job_title": body.job_title,
            "reporting_manager": body.reporting_manager,
            "letter_text": letter,
            "approval_status": "Draft",
        }
    )
    db.update_candidate_status(body.candidate_id, "Offer Generated")
    db.log_audit("OFFER_DRAFT", "offers", oid, role, str(body.candidate_id))
    return {"id": oid, "letter_text": letter}


@app.patch("/api/offers/{offer_id}/status")
def api_offer_status(
    offer_id: int,
    body: OfferStatusUpdate,
    role: InternalRole,
):
    db.update_offer_status(offer_id, body.approval_status)
    with db.get_conn() as conn:
        o = conn.execute("SELECT candidate_id FROM offers WHERE id = ?", (offer_id,)).fetchone()
    if o and body.approval_status in ("Approved", "Sent"):
        db.update_candidate_status(o["candidate_id"], "Offer Generated")
    db.log_audit("OFFER_STATUS", "offers", offer_id, role, body.approval_status)
    return {"ok": True}


@app.get("/api/onboarding/candidates")
def api_onboarding_people(_role: InternalRole):
    rows = db.onboarding_candidates()
    return [_row_to_dict(r) for r in rows]


@app.get("/api/onboarding/{candidate_id}/tasks")
def api_onboarding_tasks(candidate_id: int, _role: InternalRole):
    rows = db.get_onboarding_tasks(candidate_id)
    return [_row_to_dict(r) for r in rows]


@app.patch("/api/onboarding/tasks/{task_id}")
def api_task_toggle(
    task_id: int,
    body: OnboardingTaskUpdate,
    role: InternalRole,
):
    db.toggle_onboarding_task(task_id, 1 if body.completed else 0)
    db.log_audit("ONBOARD_TASK", "onboarding_tasks", task_id, role, "toggle")
    return {"ok": True}


@app.get("/api/audit")
def api_audit(_role: InternalRole):
    rows = db.recent_audit(30)
    return [_row_to_dict(r) for r in rows]


@app.get("/api/ai/onboarding")
def api_onboarding_faq(_role: InternalRole, q: str = ""):
    return {"answer": mock_ai.onboarding_chatbot_response(q)}
