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

## B. Backend → Render free tier (recommended $0 path)

Render's free tier runs Python web services with zero cost, but has no MySQL — this app falls back to **SQLite automatically when `DB_HOST` is unset**, so no database service is needed.

1. In [render.com](https://render.com): **New → Web Service** → connect the repo.
2. Configure:
   - **Root Directory:** `backend`
   - **Runtime:** Python 3
   - **Build command:** `pip install -r requirements.txt`
   - **Start command:** `gunicorn app.main:app -k uvicorn.workers.UvicornWorker -b 0.0.0.0:$PORT --workers 2 --timeout 120`
   - Env vars (all optional): `CLASSIFIER_PROVIDER=openai` + `OPENAI_API_KEY`/`OPENAI_BASE_URL` (defaults to rule-based), `ALLOWED_ORIGINS=https://<project>.vercel.app`
3. Create the service → Render gives you `https://<app>.onrender.com`. Run `python -m app.seed` once from the Render shell if you want the 60-ticket demo data (tables are created automatically on first start).
4. Use that URL as `VITE_API_URL` in Vercel.

> ⚠️ **Free-tier caveats:** the service sleeps after 15 min idle (first request takes ~30–60 s to wake), and the SQLite file is **ephemeral** — data resets on redeploy. Add a Render disk or upgrade to paid for persistence.

### Alternative: Railway / Render paid / Fly.io (MySQL)
Set `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD` from your managed MySQL and the app uses it automatically.

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
