# Deploying the AI Ticket Routing System

The app has two parts:

| Part | Stack | Where it can run |
|---|---|---|
| Frontend (dashboard) | React + Vite static build | **Vercel / Netlify / any static host** |
| Backend (API + classifier + routing) | FastAPI + MySQL, long-running | **Railway / Render / Fly.io / any Python host** |

## A. Frontend → Vercel (free `yourapp.vercel.app` domain)

1. Push this repo to **your** GitHub account.
2. Go to [vercel.com](https://vercel.com) → **Add New → Project** → import the repo.
3. Configure:
   - **Root Directory:** `frontend`
   - Framework preset: Vite (auto-detected)
   - **Environment variable:** `VITE_API_URL` = your backend's public URL (see section B), e.g. `https://your-backend.up.railway.app`
     - ⚠️ No trailing slash.
4. Deploy → you get `https://<project>.vercel.app` free.

> If `VITE_API_URL` is omitted, the frontend calls `/api` on its own origin (same-origin mode — use this when backend and frontend share a domain).

## B. Backend → Railway (or Render/Fly)

The backend needs a persistent Python process + MySQL — it cannot run on Vercel serverless.

1. In [Railway](https://railway.app): **New Project → Deploy from GitHub repo**.
2. Set:
   - **Root Directory:** `backend`
   - **Start command:** `gunicorn app.main:app -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000`
   - Env vars: `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD` (use Railway's MySQL plugin values), `CLASSIFIER_PROVIDER=local` (or `openai` + `OPENAI_API_KEY`/`OPENAI_BASE_URL`), `ALLOWED_ORIGINS=https://<project>.vercel.app`
3. Tables are created automatically on startup (`Base.metadata.create_all`). Optionally seed demo data: run `python -m app.seed` once.
4. Generate a public domain in Railway → use it as `VITE_API_URL` in Vercel.

**Deploy order matters:** backend first (get its URL), then frontend pointing at it.

## C. Local / dev

```bash
# backend
cd backend && python -m venv venv && venv/bin/pip install -r requirements.txt
venv/bin/uvicorn app.main:app --port 8000
venv/bin/python -m app.seed   # demo data

# frontend
cd frontend && npm install && npm run dev   # proxies /api → localhost:8000
```
