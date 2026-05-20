# Mint Street

> *Where new money meets new ideas.*

Mint Street is a startup intelligence platform tracking funding rounds, M&A, IPOs, policy shifts, and deep-tech developments across India and globally. It pulls signal from trusted publishers, rewrites every story in-house, and surfaces what matters to operators, investors, and policymakers.

![logo](frontend/public/logo-full.svg)

## Stack

- **Frontend:** React 18, Tailwind CSS, craco, react-router 6
- **Backend:** FastAPI (Python 3.11+), Motor (async MongoDB)
- **Database:** MongoDB Atlas (or self-hosted)
- **Workers:** Celery + Beat (RSS scraping, summary expansion, Telegram digest)
- **Hosting:** Railway (`railway.toml` provided)

## Quick start

### 1. Frontend

```bash
cd frontend
npm install              # uses legacy-peer-deps via .npmrc
npm start                # http://localhost:3001 (PORT pinned in .env.local)
```

If port 3001 is busy, edit `frontend/.env.local` or pass `PORT=3002 npm start`.

### 2. Backend

```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env     # fill in real values, see "Env vars" below
uvicorn server:app --reload --port 8000
```

On first boot, if `db.news` is empty the server seeds it with **100 original
article summaries** from `backend/seed_articles.py` so the feed renders out of the box.

### 3. Point the frontend at the backend

Create `frontend/.env`:

```
REACT_APP_BACKEND_URL=http://localhost:8000
```

## Env vars (backend)

See `backend/.env.example`. Required: `MONGO_URL`, `DB_NAME`. Optional integrations: `EMERGENT_LLM_KEY`, `AUTHKEY_API_KEY` (OTP), `IMAGEKIT_*` (uploads), `GEMINI_API_KEY` (translation), `CORS_ORIGINS`.

Never commit `.env`. `.gitignore` already excludes `.env`, `.env.*`, and `frontend/.env*`.

## Brand & design

- **Primary:** `#F26B1F` (tangerine)
- **Dark hover:** `#C2410B`
- **Light tint:** `#FFF1E6`
- **Paper background:** `#FAF7F1`
- **Dark mode background:** `#1C1410`
- **Accent (urgent/breaking):** `#F5C13D` (saffron)
- **Display font:** Fraunces — **Body:** Inter

Brand assets in `frontend/public/`: `logo.svg` (square mark), `logo-full.svg` (wordmark + tagline).

## Editorial standards

Every article summary on Mint Street is original — written by our editorial team or rephrased in-house from our own reporting notes. We attribute every external story with a link back to the original publisher. We do **not** republish copy verbatim, paraphrase to launder copyright, or strip watermarks/credits from third-party imagery. Stock photography is sourced exclusively from royalty-free providers (Pexels).

## Repo layout

```
backend/
  server.py              # FastAPI app + startup seeding
  seed_articles.py       # 40 base articles + import 4 batch files
  seed/                  # 4×15 batched seeds (funding/trending/newindia/global)
  routes/                # /api/* endpoints (news, auth, scraper, …)
  models.py              # Pydantic schemas
  database.py            # Mongo client + category map
frontend/
  src/components/        # Header, Footer, NewsCard, BottomNav, CategoryChips
  src/pages/             # NewsFeed (bento), ArticlePage, About, Contact, …
  src/App.js             # Router + AppContext
  public/                # index.html, logo.svg, logo-full.svg, rss.xml, robots
```

## Scripts

- `cd frontend && npm run build` — production bundle into `frontend/build/`
- `cd backend && python seed_articles.py` — print article count + sample
- `cd backend && python -m compileall .` — syntax-check all modules

## Deploy

Railway picks up `railway.toml`. Set the env vars listed above on the Railway service. Atlas IP allow-list `0.0.0.0/0` if you need Railway's dynamic egress.

## License

© 2026 Mint Street. All rights reserved.
