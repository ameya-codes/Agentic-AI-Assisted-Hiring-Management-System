# HireFlow AI — deployment guide

The app has **two parts**: a **static React (Vite) frontend** and a **FastAPI + SQLite API**.  
**Vercel** is ideal for the frontend. **FastAPI cannot run as a normal always-on server on Vercel’s default Node/static product** (it needs a separate Python host, e.g. **Render**, **Railway**, or **Fly.io**).

Your Vercel account (e.g. mr.ameyanaik@gmail.com) is only used in the browser — this repo cannot log in for you. Follow the steps below after pushing the code to **GitHub**.

---

## Part A — Deploy the API (Render, free tier)

1. Push this repository to **GitHub** (if it is not already).
2. Go to [Render](https://render.com) and sign up / log in (GitHub login is fine).
3. **New → Blueprint** (or **New Web Service**).
   - If using Blueprint: connect the repo and select **`render.yaml`** at the repo root.
   - If using Web Service manually:
     - **Root directory:** leave empty (repo root) or `.`
     - **Runtime:** Python 3
     - **Build command:** `pip install -r requirements.txt`
     - **Start command:** `uvicorn api.main:app --host 0.0.0.0 --port $PORT`
     - **Health check path:** `/api/health`
4. In the Render service **Environment** tab, add:
   - `OPENAI_API_KEY` (optional; omit to use offline heuristics only)
5. Wait for deploy. Copy the service URL, e.g. `https://hireflow-ai-api.onrender.com`.

**Note:** On Render’s free tier, the disk is **ephemeral** — SQLite (`hiring_poc.db`) resets when the service restarts or sleeps. Fine for a class POC; use a managed DB for production.

**CORS:** The API allows `https://*.vercel.app` plus localhost. To allow a **custom domain** on Vercel, set on Render:

`CORS_EXTRA_ORIGINS=https://yourdomain.com`

(comma-separated if multiple).

---

## Part B — Deploy the website (Vercel)

1. Go to [Vercel](https://vercel.com) and log in with **mr.ameyanaik@gmail.com** (or your linked GitHub).
2. **Add New… → Project** → **Import** your GitHub repository.
3. **Root Directory:** set to **`frontend`** (important — Vite app lives there).
4. **Framework Preset:** Vite (auto-detected).
5. **Build & Output settings:** defaults are usually:
   - Build command: `npm run build`
   - Output directory: `dist`
6. **Environment Variables** (Production — required for API calls from the browser):

   | Name            | Value |
   |-----------------|--------|
   | `VITE_API_URL`  | Your Render API base **with no trailing slash**, e.g. `https://hireflow-ai-api.onrender.com` |

   The frontend uses `VITE_API_URL` at **build time**; after changing it, **Redeploy** in Vercel.

7. Click **Deploy**.

8. Open the `.vercel.app` URL. Login and flows should hit your Render API.

`frontend/vercel.json` adds SPA **rewrites** so React Router paths (e.g. `/app/dashboard`) work on refresh.

---

## Part C — Verify

- Browser: open `https://<your-project>.vercel.app`
- Open DevTools → Network: API calls should go to `https://<your-render-service>.onrender.com/api/...`
- `GET https://<render>/api/health` should return `{"ok":true}`

---

## Optional: Streamlit on Streamlit Cloud

`app.py` is separate from the Vercel site. To host Streamlit, use [Streamlit Community Cloud](https://streamlit.io/cloud) with **main file** `app.py` and root = repo root (not `frontend`).

---

## Troubleshooting

| Issue | What to check |
|--------|----------------|
| CORS errors in browser | `VITE_API_URL` correct; Render deployed; `CORS_EXTRA_ORIGINS` if using a custom domain |
| 404 on `/app/...` refresh | Root Directory must be `frontend` (so `vercel.json` is picked up) |
| API 502 on Render | Logs on Render; `requirements.txt` installs; start command uses `$PORT` |
| Empty data | First request initializes DB; free Render **cold start** can take ~30s |

---

## Security reminder

Do **not** commit `.env` or API keys. Set secrets only in **Render** / **Vercel** environment UIs.
