"""
SQLite persistence for the Hiring Management POC.
Beginner-friendly: plain SQL, no ORM.
"""

import sqlite3
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).parent / "hiring_poc.db"


def _now() -> str:
    return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")


@contextmanager
def get_conn():
    conn = sqlite3.connect(DB_PATH, timeout=30.0)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db() -> None:
    with get_conn() as conn:
        c = conn.cursor()
        c.executescript(
            """
            CREATE TABLE IF NOT EXISTS jobs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                department TEXT,
                location TEXT,
                salary_min REAL,
                salary_max REAL,
                experience_level TEXT,
                required_skills TEXT,
                description TEXT,
                status TEXT DEFAULT 'Open',
                created_at TEXT
            );

            CREATE TABLE IF NOT EXISTS candidates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_id INTEGER NOT NULL REFERENCES jobs(id),
                name TEXT NOT NULL,
                email TEXT,
                resume_text TEXT,
                status TEXT DEFAULT 'New',
                created_at TEXT
            );

            CREATE TABLE IF NOT EXISTS screenings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                candidate_id INTEGER NOT NULL REFERENCES candidates(id) UNIQUE,
                skills TEXT,
                experience TEXT,
                education TEXT,
                certifications TEXT,
                strengths TEXT,
                weaknesses TEXT,
                match_score INTEGER,
                recommendation TEXT,
                created_at TEXT
            );

            CREATE TABLE IF NOT EXISTS interviews (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                candidate_id INTEGER NOT NULL REFERENCES candidates(id),
                interviewer_name TEXT,
                scheduled_at TEXT,
                interview_type TEXT,
                invitation_email TEXT,
                tech_questions TEXT,
                behavioral_questions TEXT,
                created_at TEXT
            );

            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                interview_id INTEGER NOT NULL REFERENCES interviews(id),
                technical_feedback TEXT,
                communication_feedback TEXT,
                overall_rating INTEGER,
                hire_decision TEXT,
                ai_summary TEXT,
                sentiment TEXT,
                candidate_strengths TEXT,
                candidate_risks TEXT,
                final_recommendation TEXT,
                created_at TEXT
            );

            CREATE TABLE IF NOT EXISTS offers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                candidate_id INTEGER NOT NULL REFERENCES candidates(id),
                salary REAL,
                start_date TEXT,
                job_title TEXT,
                reporting_manager TEXT,
                letter_text TEXT,
                approval_status TEXT DEFAULT 'Draft',
                created_at TEXT
            );

            CREATE TABLE IF NOT EXISTS onboarding_tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                candidate_id INTEGER NOT NULL REFERENCES candidates(id),
                task_name TEXT NOT NULL,
                completed INTEGER DEFAULT 0,
                sort_order INTEGER DEFAULT 0
            );

            CREATE TABLE IF NOT EXISTS audit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                action TEXT,
                entity_type TEXT,
                entity_id INTEGER,
                user_role TEXT,
                details TEXT,
                created_at TEXT
            );
            """
        )


def log_audit(action: str, entity_type: str, entity_id: int | None, user_role: str, details: str) -> None:
    with get_conn() as conn:
        conn.execute(
            """
            INSERT INTO audit_logs (action, entity_type, entity_id, user_role, details, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (action, entity_type, entity_id, user_role, details, _now()),
        )


def seed_if_empty() -> None:
    with get_conn() as conn:
        row = conn.execute("SELECT COUNT(*) AS c FROM jobs").fetchone()
        if row and row["c"] > 0:
            return

        now = _now()
        conn.execute(
            """
            INSERT INTO jobs (title, department, location, salary_min, salary_max, experience_level,
                required_skills, description, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                "Senior Backend Engineer",
                "Engineering",
                "Remote (US)",
                140000,
                175000,
                "Senior",
                "Python, FastAPI, PostgreSQL, AWS, system design",
                "We are hiring a senior backend engineer to design and scale our hiring platform APIs.",
                "Open",
                now,
            ),
        )
        conn.execute(
            """
            INSERT INTO jobs (title, department, location, salary_min, salary_max, experience_level,
                required_skills, description, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                "Product Analyst",
                "Product",
                "New York, NY",
                95000,
                115000,
                "Mid",
                "SQL, experimentation, stakeholder management, dashboards",
                "Drive product decisions through data and partner with HR stakeholders on roadmap.",
                "Open",
                now,
            ),
        )

        job1 = conn.execute("SELECT id FROM jobs WHERE title = ?", ("Senior Backend Engineer",)).fetchone()[0]
        job2 = conn.execute("SELECT id FROM jobs WHERE title = ?", ("Product Analyst",)).fetchone()[0]

        candidates_seed = [
            (job1, "Alex Rivera", "alex.rivera@email.com", "Shortlisted", 88, "Proceed to Interview"),
            (job1, "Jordan Lee", "jordan.lee@email.com", "Interview Scheduled", 76, "Proceed to Interview"),
            (job1, "Sam Patel", "sam.patel@email.com", "New", 62, "Hold"),
            (job2, "Casey Morgan", "casey.morgan@email.com", "Interview Completed", 91, "Proceed to Interview"),
            (job2, "Riley Chen", "riley.chen@email.com", "Rejected", 41, "Reject"),
        ]

        for job_id, name, email, status, score, rec in candidates_seed:
            resume = (
                f"Resume for {name}: experienced professional with relevant skills. "
                f"Education: BS Computer Science. Projects in data and backend systems."
            )
            cur = conn.execute(
                """
                INSERT INTO candidates (job_id, name, email, resume_text, status, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (job_id, name, email, resume, status, now),
            )
            cid = cur.lastrowid
            conn.execute(
                """
                INSERT INTO screenings (candidate_id, skills, experience, education, certifications,
                    strengths, weaknesses, match_score, recommendation, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    cid,
                    "Python, SQL, APIs",
                    "5+ years in software roles",
                    "BS Computer Science",
                    "AWS Certified Developer",
                    "Strong ownership; clear communication",
                    "Limited domain depth in hiring tech",
                    score,
                    rec,
                    now,
                ),
            )

        # Interviews for first two backend candidates
        c_rows = conn.execute(
            "SELECT id FROM candidates WHERE name IN ('Alex Rivera', 'Jordan Lee') ORDER BY id"
        ).fetchall()
        if len(c_rows) >= 2:
            cid1, cid2 = c_rows[0][0], c_rows[1][0]
            conn.execute(
                """
                INSERT INTO interviews (candidate_id, interviewer_name, scheduled_at, interview_type,
                    invitation_email, tech_questions, behavioral_questions, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    cid1,
                    "Jamie Ortiz",
                    "2026-05-15 14:00:00",
                    "Technical",
                    "Dear Alex, your technical interview is scheduled...",
                    "1. Design a rate-limited API\n2. Explain DB indexing tradeoffs",
                    "1. Tell me about a complex tradeoff\n2. Handling disagreement with PM",
                    now,
                ),
            )
            conn.execute(
                """
                INSERT INTO interviews (candidate_id, interviewer_name, scheduled_at, interview_type,
                    invitation_email, tech_questions, behavioral_questions, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    cid2,
                    "Taylor Kim",
                    "2026-05-18 10:30:00",
                    "Behavioral",
                    "Dear Jordan, looking forward to speaking...",
                    "Walk through a recent backend migration",
                    "Ownership example; working with ambiguity",
                    now,
                ),
            )

        casey_row = conn.execute("SELECT id FROM candidates WHERE name = ?", ("Casey Morgan",)).fetchone()
        if casey_row:
            casey_cid = casey_row[0]
            cur_iv = conn.execute(
                """
                INSERT INTO interviews (candidate_id, interviewer_name, scheduled_at, interview_type,
                    invitation_email, tech_questions, behavioral_questions, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    casey_cid,
                    "Morgan Singh",
                    "2026-05-10 16:00:00",
                    "Final",
                    "Dear Casey, confirming your final round...",
                    "Deep dive: metrics framework and experiment design",
                    "Stakeholder storytelling; prioritization under constraints",
                    now,
                ),
            )
            casey_interview_id = cur_iv.lastrowid
            conn.execute(
                """
                INSERT INTO feedback (interview_id, technical_feedback, communication_feedback, overall_rating,
                    hire_decision, ai_summary, sentiment, candidate_strengths, candidate_risks, final_recommendation, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    casey_interview_id,
                    "Strong analytical framing; clear examples of experimentation.",
                    "Excellent structure and executive presence.",
                    5,
                    "Hire",
                    "Casey demonstrates strong product analytics judgment.",
                    "Positive",
                    "Metrics ownership, SQL depth, cross-functional communication",
                    "Limited hands-on eng depth—acceptable for role level",
                    "Recommend offer pending comp approval",
                    now,
                ),
            )

        # One offer example for Casey Morgan (positive path)
        casey = conn.execute("SELECT id FROM candidates WHERE name = ?", ("Casey Morgan",)).fetchone()
        if casey:
            conn.execute(
                """
                INSERT INTO offers (candidate_id, salary, start_date, job_title, reporting_manager,
                    letter_text, approval_status, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    casey[0],
                    108000,
                    "2026-06-02",
                    "Product Analyst",
                    "Jordan Lee (Product Lead)",
                    "Dear Casey,\n\nWe are pleased to extend an offer...",
                    "Approved",
                    now,
                ),
            )
            offer_tasks = [
                ("Sign offer letter", 0, 1),
                ("Submit ID documents", 0, 2),
                ("Complete background verification", 0, 3),
                ("Create company email", 0, 4),
                ("Laptop/IT setup", 0, 5),
                ("HR orientation", 0, 6),
                ("Team introduction", 0, 7),
            ]
            for task, done, ord_ in offer_tasks:
                conn.execute(
                    """
                    INSERT INTO onboarding_tasks (candidate_id, task_name, completed, sort_order)
                    VALUES (?, ?, ?, ?)
                    """,
                    (casey[0], task, done, ord_),
                )

        conn.execute(
            """
            INSERT INTO audit_logs (action, entity_type, entity_id, user_role, details, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                "SEED",
                "system",
                None,
                "system",
                "Database seeded with sample jobs, candidates, interviews, offer.",
                _now(),
            ),
        )


def list_jobs():
    with get_conn() as conn:
        return conn.execute(
            "SELECT * FROM jobs ORDER BY created_at DESC"
        ).fetchall()


def list_open_jobs_public():
    """Open roles for the external careers view — no compensation fields."""
    with get_conn() as conn:
        return conn.execute(
            """
            SELECT id, title, department, location, experience_level, required_skills, description
            FROM jobs
            WHERE status = 'Open'
            ORDER BY created_at DESC
            """
        ).fetchall()


def list_jobs_with_applicant_counts(job_id: int | None = None):
    with get_conn() as conn:
        base = """
            SELECT j.id, j.title, j.status, j.department, j.location,
                   COUNT(c.id) AS applicant_count
            FROM jobs j
            LEFT JOIN candidates c ON c.job_id = j.id
        """
        if job_id is not None:
            return conn.execute(
                base + " WHERE j.id = ? GROUP BY j.id ORDER BY j.created_at DESC",
                (job_id,),
            ).fetchall()
        return conn.execute(
            base + " GROUP BY j.id ORDER BY j.created_at DESC",
        ).fetchall()


def applications_for_email(email: str):
    key = (email or "").strip().lower()
    if not key:
        return []
    with get_conn() as conn:
        return conn.execute(
            """
            SELECT c.id, c.name, c.email, c.status, c.created_at AS applied_at,
                   j.id AS job_id, j.title AS job_title
            FROM candidates c
            JOIN jobs j ON j.id = c.job_id
            WHERE LOWER(TRIM(c.email)) = ?
            ORDER BY c.created_at DESC
            """,
            (key,),
        ).fetchall()


def list_applicants_for_staff(job_id: int | None = None):
    """All applicants with job context for hiring manager / recruiter views."""
    with get_conn() as conn:
        base = """
            SELECT c.id AS candidate_id, c.name, c.email, c.status, c.created_at AS applied_at,
                   j.id AS job_id, j.title AS job_title, j.status AS job_status, j.department AS job_department,
                   s.match_score, s.recommendation
            FROM candidates c
            JOIN jobs j ON j.id = c.job_id
            LEFT JOIN screenings s ON s.candidate_id = c.id
        """
        if job_id is not None:
            return conn.execute(
                base + " WHERE j.id = ? ORDER BY c.created_at DESC",
                (job_id,),
            ).fetchall()
        return conn.execute(
            base + " ORDER BY j.created_at DESC, c.created_at DESC",
        ).fetchall()


def insert_job(data: dict) -> int:
    with get_conn() as conn:
        cur = conn.execute(
            """
            INSERT INTO jobs (title, department, location, salary_min, salary_max, experience_level,
                required_skills, description, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'Open', ?)
            """,
            (
                data["title"],
                data["department"],
                data["location"],
                data["salary_min"],
                data["salary_max"],
                data["experience_level"],
                data["required_skills"],
                data["description"],
                _now(),
            ),
        )
        return cur.lastrowid


def insert_candidate_screening(
    job_id: int,
    name: str,
    email: str,
    resume_text: str,
    screening: dict,
) -> int:
    with get_conn() as conn:
        cur = conn.execute(
            """
            INSERT INTO candidates (job_id, name, email, resume_text, status, created_at)
            VALUES (?, ?, ?, ?, 'New', ?)
            """,
            (job_id, name, email, resume_text, _now()),
        )
        cid = cur.lastrowid
        conn.execute(
            """
            INSERT INTO screenings (candidate_id, skills, experience, education, certifications,
                strengths, weaknesses, match_score, recommendation, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                cid,
                screening["skills"],
                screening["experience"],
                screening["education"],
                screening["certifications"],
                screening["strengths"],
                screening["weaknesses"],
                screening["match_score"],
                screening["recommendation"],
                _now(),
            ),
        )
        return cid


def update_candidate_status(candidate_id: int, status: str) -> None:
    with get_conn() as conn:
        conn.execute(
            "UPDATE candidates SET status = ? WHERE id = ?",
            (status, candidate_id),
        )


def ranked_candidates(job_id: int | None = None):
    with get_conn() as conn:
        q = """
            SELECT c.id AS candidate_id, c.name, c.status, j.title AS job_title,
                   s.match_score, s.skills, s.recommendation
            FROM candidates c
            JOIN jobs j ON j.id = c.job_id
            LEFT JOIN screenings s ON s.candidate_id = c.id
        """
        params: tuple = ()
        if job_id is not None:
            q += " WHERE c.job_id = ?"
            params = (job_id,)
        q += " ORDER BY (s.match_score IS NULL), s.match_score DESC, c.name"
        return conn.execute(q, params).fetchall()


def shortlisted_candidates(job_id: int | None = None):
    with get_conn() as conn:
        q = """
            SELECT c.id, c.name, j.title AS job_title
            FROM candidates c
            JOIN jobs j ON j.id = c.job_id
            WHERE c.status IN ('Shortlisted', 'Interview Scheduled', 'Interview Completed')
        """
        params: tuple = ()
        if job_id is not None:
            q += " AND c.job_id = ?"
            params = (job_id,)
        q += " ORDER BY c.name"
        return conn.execute(q, params).fetchall()


def insert_interview(data: dict) -> int:
    with get_conn() as conn:
        cur = conn.execute(
            """
            INSERT INTO interviews (candidate_id, interviewer_name, scheduled_at, interview_type,
                invitation_email, tech_questions, behavioral_questions, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                data["candidate_id"],
                data["interviewer_name"],
                data["scheduled_at"],
                data["interview_type"],
                data["invitation_email"],
                data["tech_questions"],
                data["behavioral_questions"],
                _now(),
            ),
        )
        return cur.lastrowid


def list_interviews_for_feedback(job_id: int | None = None):
    with get_conn() as conn:
        q = """
            SELECT i.id, i.candidate_id, c.name AS candidate_name, j.title AS job_title,
                   i.interviewer_name, i.scheduled_at, i.interview_type,
                   (SELECT COUNT(*) FROM feedback f WHERE f.interview_id = i.id) AS has_feedback
            FROM interviews i
            JOIN candidates c ON c.id = i.candidate_id
            JOIN jobs j ON j.id = c.job_id
        """
        params: tuple = ()
        if job_id is not None:
            q += " WHERE c.job_id = ?"
            params = (job_id,)
        q += " ORDER BY i.scheduled_at DESC"
        return conn.execute(q, params).fetchall()


def insert_feedback(data: dict) -> int:
    with get_conn() as conn:
        cur = conn.execute(
            """
            INSERT INTO feedback (interview_id, technical_feedback, communication_feedback, overall_rating,
                hire_decision, ai_summary, sentiment, candidate_strengths, candidate_risks, final_recommendation, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                data["interview_id"],
                data["technical_feedback"],
                data["communication_feedback"],
                data["overall_rating"],
                data["hire_decision"],
                data["ai_summary"],
                data["sentiment"],
                data["candidate_strengths"],
                data["candidate_risks"],
                data["final_recommendation"],
                _now(),
            ),
        )
        return cur.lastrowid


def candidates_for_offer(job_id: int | None = None):
    """Candidates with positive-ish feedback (Hire or Maybe) and no duplicate open offer logic simplified."""
    with get_conn() as conn:
        q = """
            SELECT DISTINCT c.id, c.name, j.title AS job_title, f.hire_decision, f.final_recommendation
            FROM candidates c
            JOIN jobs j ON j.id = c.job_id
            JOIN interviews i ON i.candidate_id = c.id
            JOIN feedback f ON f.interview_id = i.id
            WHERE f.hire_decision IN ('Hire', 'Maybe')
        """
        params: tuple = ()
        if job_id is not None:
            q += " AND c.job_id = ?"
            params = (job_id,)
        q += " ORDER BY c.name"
        return conn.execute(q, params).fetchall()


def insert_offer(data: dict) -> int:
    with get_conn() as conn:
        cur = conn.execute(
            """
            INSERT INTO offers (candidate_id, salary, start_date, job_title, reporting_manager,
                letter_text, approval_status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                data["candidate_id"],
                data["salary"],
                data["start_date"],
                data["job_title"],
                data["reporting_manager"],
                data["letter_text"],
                data["approval_status"],
                _now(),
            ),
        )
        return cur.lastrowid


def update_offer_status(offer_id: int, status: str) -> None:
    with get_conn() as conn:
        conn.execute("UPDATE offers SET approval_status = ? WHERE id = ?", (status, offer_id))


def list_offers(job_id: int | None = None):
    with get_conn() as conn:
        q = """
            SELECT o.*, c.name AS candidate_name
            FROM offers o
            JOIN candidates c ON c.id = o.candidate_id
        """
        params: tuple = ()
        if job_id is not None:
            q += " WHERE c.job_id = ?"
            params = (job_id,)
        q += " ORDER BY o.created_at DESC"
        return conn.execute(q, params).fetchall()


def onboarding_candidates():
    with get_conn() as conn:
        return conn.execute(
            """
            SELECT DISTINCT c.id, c.name, o.approval_status
            FROM candidates c
            JOIN offers o ON o.candidate_id = c.id
            WHERE o.approval_status IN ('Approved', 'Sent')
            ORDER BY c.name
            """
        ).fetchall()


def get_onboarding_tasks(candidate_id: int):
    with get_conn() as conn:
        rows = conn.execute(
            """
            SELECT id, task_name, completed, sort_order
            FROM onboarding_tasks WHERE candidate_id = ?
            ORDER BY sort_order, id
            """,
            (candidate_id,),
        ).fetchall()
        if rows:
            return rows
        # Default checklist if none stored
        default = [
            "Sign offer letter",
            "Submit ID documents",
            "Complete background verification",
            "Create company email",
            "Laptop/IT setup",
            "HR orientation",
            "Team introduction",
        ]
        for idx, name in enumerate(default, start=1):
            conn.execute(
                """
                INSERT INTO onboarding_tasks (candidate_id, task_name, completed, sort_order)
                VALUES (?, ?, 0, ?)
                """,
                (candidate_id, name, idx),
            )
        return conn.execute(
            """
            SELECT id, task_name, completed, sort_order
            FROM onboarding_tasks WHERE candidate_id = ?
            ORDER BY sort_order, id
            """,
            (candidate_id,),
        ).fetchall()


def toggle_onboarding_task(task_id: int, completed: int) -> None:
    with get_conn() as conn:
        conn.execute(
            "UPDATE onboarding_tasks SET completed = ? WHERE id = ?",
            (completed, task_id),
        )


def dashboard_stats(job_id: int | None = None):
    with get_conn() as conn:
        if job_id is None:
            open_jobs = conn.execute(
                "SELECT COUNT(*) FROM jobs WHERE status = 'Open'"
            ).fetchone()[0]
            total_candidates = conn.execute("SELECT COUNT(*) FROM candidates").fetchone()[0]
            shortlisted = conn.execute(
                "SELECT COUNT(*) FROM candidates WHERE status = 'Shortlisted'"
            ).fetchone()[0]
            interviews = conn.execute("SELECT COUNT(*) FROM interviews").fetchone()[0]
            offers = conn.execute("SELECT COUNT(*) FROM offers").fetchone()[0]
            pipeline = conn.execute(
                "SELECT status, COUNT(*) AS cnt FROM candidates GROUP BY status"
            ).fetchall()
        else:
            row = conn.execute(
                "SELECT status FROM jobs WHERE id = ?",
                (job_id,),
            ).fetchone()
            open_jobs = 1 if row and row["status"] == "Open" else 0
            total_candidates = conn.execute(
                "SELECT COUNT(*) FROM candidates WHERE job_id = ?",
                (job_id,),
            ).fetchone()[0]
            shortlisted = conn.execute(
                "SELECT COUNT(*) FROM candidates WHERE job_id = ? AND status = 'Shortlisted'",
                (job_id,),
            ).fetchone()[0]
            interviews = conn.execute(
                """
                SELECT COUNT(*) FROM interviews i
                JOIN candidates c ON c.id = i.candidate_id
                WHERE c.job_id = ?
                """,
                (job_id,),
            ).fetchone()[0]
            offers = conn.execute(
                """
                SELECT COUNT(*) FROM offers o
                JOIN candidates c ON c.id = o.candidate_id
                WHERE c.job_id = ?
                """,
                (job_id,),
            ).fetchone()[0]
            pipeline = conn.execute(
                """
                SELECT status, COUNT(*) AS cnt FROM candidates
                WHERE job_id = ? GROUP BY status
                """,
                (job_id,),
            ).fetchall()
        return {
            "open_jobs": open_jobs,
            "total_candidates": total_candidates,
            "shortlisted": shortlisted,
            "interviews": interviews,
            "offers": offers,
            "pipeline": pipeline,
        }


def recent_audit(limit: int = 20):
    with get_conn() as conn:
        return conn.execute(
            "SELECT * FROM audit_logs ORDER BY id DESC LIMIT ?",
            (limit,),
        ).fetchall()
