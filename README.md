# HireFlow AI — Agentic Hiring Management (POC)

A **Software Analysis & Design** semester project: **HireFlow AI** — an **enterprise-style hiring workflow** with **AI-assisted drafts** and **human approval gates**. Run **Streamlit** or **React + FastAPI**. Not a production HR system.

**Deploy (Vercel + API):** see **[DEPLOYMENT.md](DEPLOYMENT.md)** — frontend on Vercel (`frontend/` root), FastAPI on Render (or similar); set `VITE_API_URL` on Vercel to your API URL.

## OpenAI (ChatGPT API) — optional

**Never put API keys in source code or in chat.** If a key was exposed, revoke it in the [OpenAI key dashboard](https://platform.openai.com/api-keys) and create a new one.

1. Copy `.env.example` to `.env` in the project root.  
2. Set `OPENAI_API_KEY=sk-...` in `.env` only (`.env` is gitignored).  
3. Restart the API / Streamlit process.  

With a valid key, **all agent helpers in `mock_ai.py`** try the LLM first (via `llm.py`); if the call fails or no key is set, they **fall back to local logic** so demos work offline.

**Prompts for your write-up:** see `prompts.py` — each hiring subprocess has a **system prompt** and a structured **user payload** (JSON) so you can document “required prompt” per step as the assignment asks.

**“Unlimited Copilot” in the assignment:** that usually means *assume you can call a capable LLM* — in code we use the **OpenAI Chat Completions API** (`gpt-4o-mini` by default). You could swap `llm.py` to **Azure OpenAI** or another vendor without changing the rest of the app.

### Process → LLM vs non-LLM (for design docs)

| Hiring subprocess | LLM support (this repo) | Non-LLM / human |
|-------------------|-------------------------|-----------------|
| Job description draft | Yes (`generate_job_description`) | Final posting approval, comp bands |
| Resume screening | Yes (`screen_resume`) | Human shortlist / legal |
| Ranking order | Heuristic sort by score | Pipeline status changes |
| Interview invite + questions | Yes (`generate_interview_email`, `generate_interview_questions`) | Sending email, calendar truth |
| Feedback summary | Yes (`summarize_feedback`) | Hire / no-hire decision |
| Offer letter text | Yes (`generate_offer_letter`) | **Salary number**, legal sign-off |
| Onboarding FAQ | Yes (`onboarding_chatbot_response`) | Policy source of truth, IT tickets |
| Audit / DB / RBAC | No | System layer |

## What you get

- **SQLite** persistence (`hiring_poc.db` in the project folder) — shared by Streamlit and the React app  
- **AI layer**: optional **OpenAI**-backed agents (`OPENAI_API_KEY` in `.env`); otherwise the same flows use **local heuristics** in `mock_ai.py`  
- **Roles**: Hiring Manager, HR Recruiter, Candidate, Interviewer — scoped navigation / actions  
- **Full workflow**: requisition → screening → ranking → interview → feedback → offer → onboarding  

### Option A — Streamlit (minimal setup)

Single command UI: `app.py` + `ui_theme.py` — good for fast class demos.

## Setup

### Streamlit

1. **Python 3.10+** recommended.  
2. Create and activate a venv, then `pip install -r requirements.txt`.  
3. Run `streamlit run app.py` and open `http://localhost:8501`.

### React + FastAPI

Use this when you want **full control** over layout, components, and styling (Tailwind, component libraries, animations).

1. Same Python venv; install deps (includes FastAPI):

   ```bash
   pip install -r requirements.txt
   ```

2. **Terminal 1 — API** (from project root):

   ```bash
   uvicorn api.main:app --reload --port 8000
   ```

3. **Terminal 2 — React** (Node 18+):

   ```bash
   cd frontend
   npm install
   npm run dev
   ```

4. Open **http://127.0.0.1:5173/** (or `http://localhost:5173/`) while `npm run dev` is running. If the page does not load, the dev server is not started or the port changed — check the terminal for the exact URL (Vite may pick **5174** if 5173 is busy).

Production build: `cd frontend && npm run build` — serve `frontend/dist` with any static host and set `VITE_API_URL` to your API base URL if the app is not served from the same origin as `/api`.

### Reset demo data

Delete `hiring_poc.db` in the project folder and refresh the app. Tables are recreated and **sample data is seeded** automatically (2 jobs, 5 candidates, 3 interviews including feedback for one path, 1 approved offer, onboarding tasks).

## Suggested demo flow (for presentation)

1. **Login / Role** — choose **HR Recruiter** (screening/offers) or **Hiring Manager** (reqs/scheduling) as needed.  
2. **Job Requisition** — fill the form, click **Generate AI Job Description**, then **Save job requisition**.  
3. **Resume Screening** — pick a job, enter name/email, paste resume text (or upload `.txt`), **Run AI screening**, then **Save candidate + screening**.  
4. **Candidate Ranking** — confirm ranking by match score; use **Update candidate status** to move someone to **Shortlisted**.  
5. **Interview Scheduling** — pick a shortlisted candidate, set interviewer and time, **Generate** then **Save interview schedule**.  
6. **Interview Feedback** — pick an interview without feedback yet, enter notes, **Generate AI feedback summary**, **Save feedback**.  
7. **Offer Letter** — as HR, pick a candidate with **Hire/Maybe** feedback, enter **salary** (human-controlled), **Generate** and **Save offer**; use **Offer approvals** to move status to **Approved** or **Sent**.  
8. **Onboarding** — appears for offers in **Approved** or **Sent**; check off tasks and try the **Onboarding assistant** FAQ box.  
9. **AI Agents Overview** — slide for architecture and “what is not automated.”  

## Project files

| File        | Purpose |
|------------|---------|
| `app.py`   | Streamlit UI (optional) |
| `ui_theme.py` | Streamlit styling |
| `api/main.py` | **FastAPI** JSON API for the React app |
| `frontend/` | **React + Vite + TypeScript + Tailwind** SPA |
| `db.py`    | SQLite schema, seed data, queries |
| `mock_ai.py` | Mock agent functions (replaceable with real LLMs later) |
| `requirements.txt` | Dependencies |
| `hiring_poc.db` | SQLite file (created at runtime; safe to delete to reset) |

## Notes for students explaining the design

- **AI recommends; humans decide**: pipeline status, offer approval, and salary values are explicit human steps.  
- **Audit logs** record major actions for traceability in the POC.  
- **Resume input**: `.txt` upload and paste are supported; PDF parsing is left as an optional extension.  

## Limitations (by design)

- No real authentication or authorization service.  
- Mock AI uses heuristics and templates, not a trained model.  
- Offer text is a demo draft only, not legal advice or a binding document.  
