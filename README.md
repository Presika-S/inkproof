# Inkproof (Team NOVARA, FutureStack Round 2)

Brand governance with evidence you can verify. A draft is checked against approved rules and facts.
Every finding shows its rule, fact and exact quote, and an independent verifier decides whether it can be
shown as confirmed. Anything unverified, expired or conflicting goes to a human reviewer.

```
frontend/   React 18 + TypeScript (Vite)        -> deploy on Vercel
backend/    FastAPI + SQLAlchemy + PostgreSQL    -> deploy on Render (blueprint in render.yaml)
backend/app/engine.py   exact checks, claim/fact matching, independent verifier (pure functions, tested)
backend/app/ai.py       AI layer: the model only proposes; engine.verify() re-checks every proposal
```

## 1. Run locally

Backend (Python 3.11+):
```bash
cd backend
python -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env                                    # then edit values
set -a && source .env && set +a                         # Windows: set the variables by hand
uvicorn app.main:app --reload --port 8000
pytest                                                  # 6 tests should pass
```
Frontend (Node 18+), in a second terminal:
```bash
cd frontend
cp .env.example .env      # VITE_API_URL=http://localhost:8000
npm install
npm run dev               # http://localhost:5173
```
Demo accounts (synthetic data, created when SEED_DEMO=true): `writer@demo.test` and `reviewer@demo.test`, password `demo1234`.

## 2. Turn on the AI layer
1. Create an API key in the Anthropic Console and put it in `ANTHROPIC_API_KEY` (backend env only, never in the frontend or the repo).
2. Optionally change `AI_MODEL` (default `claude-sonnet-5-5`).
3. In the app press "Run with AI review". Without a key the app says so and rule-based review still works.
The prompt and parsing live in `backend/app/ai.py`. Proposals with an unknown rule or fact, or a quote that is not in the draft, are rejected by `verify()`.

## 3. Deploy
**Push to GitHub first** (public repo, so judges can open it):
```bash
git init && git add . && git commit -m "Inkproof round 2"
git branch -M main && git remote add origin https://github.com/<you>/inkproof.git && git push -u origin main
```
**Backend on Render**
1. Render dashboard > New > Blueprint > pick your repo. It reads `render.yaml` and creates the API and a Postgres database.
2. When asked, set `CORS_ORIGINS` to your Vercel URL (you can fill it after step Frontend) and optionally `ANTHROPIC_API_KEY`.
3. Wait for the deploy, then open `https://<your-api>.onrender.com/healthz`. You should see `{"ok": true}`.
4. Free instances sleep when idle, so the first request can take about a minute. Open the API link a few minutes before judging.
Prefer your own database (Supabase, Neon)? Skip the blueprint database and paste its connection string into `DATABASE_URL`.

**Frontend on Vercel**
1. Vercel > Add New > Project > import the same repo. Set Root Directory to `frontend`.
2. Add the environment variable `VITE_API_URL` = your Render API URL (no trailing slash).
3. Deploy. Copy the Vercel URL into Render's `CORS_ORIGINS` and redeploy the API.

## 4. Final checks before you submit
- Open the Vercel link in an incognito window and sign in with the demo writer, run the Northwind example, submit, then sign in as the demo reviewer and decide.
- Change the `SECRET_KEY` only through the host dashboard. Never commit `.env`.
- Use synthetic data only. Say honestly in your write-up what is not built yet.

## API summary
`POST /api/auth/login|register` · `GET /api/library` · `PATCH /api/rules/{id}` · `PATCH /api/facts/{id}` ·
`POST /api/review` · `POST /api/import/docx` · `POST /api/drafts` · `POST /api/drafts/{id}/findings/{i}/decision` ·
`POST /api/drafts/{id}/finalize` · `GET /api/insights` · interactive docs at `/docs`.
