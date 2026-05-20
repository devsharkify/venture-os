# Kaizer News - Way2News Style News App

## Latest Updates (Apr 2026)

### Phase 41 - 4-Paragraph Rule Enforced End-to-End (Apr 28, 2026)
- [x] **Bug**: Auto-scraped articles bypassed the 4-line rule - Gemini AI returned single-paragraph summaries with no `\n\n` breaks; the rule was only enforced on `/news/admin/push` (manual). User reported article (Diljit on Jimmy Fallon) had only 2 sentences.
- [x] **Fix in `helpers.py`**: New `ensure_min_paragraphs(text, min=4)` formats text into paragraphs by splitting on sentences (no sentence-cutting). New `expand_summary_with_ai()` calls Gemini Flash to expand thin briefs into 4-6 paragraph newspaper summaries. Strengthened `generate_ai_summary` system prompt to require explicit `\n\n` paragraph breaks.
- [x] **Fix in `routes/scraper.py`**: `save_article()` now calls `ensure_min_paragraphs` after every AI summary or fallback, and re-calls `expand_summary_with_ai` if still <4 paragraphs.
- [x] **Fix in `routes/news.py`**: `/news/scrape` uses `ensure_min_paragraphs`. New admin endpoint `POST /api/news/admin/backfill-summaries?limit=500&use_ai=false` repairs existing thin articles. Run repeatedly (use_ai=true for AI-assisted expansion of single-sentence briefs).
- [x] **Backfill executed**: 144+ articles already reformatted (no AI). Diljit article verified at 4 paragraphs. Going-forward all scraped articles auto-enforced.

### Phase 40 - Editorial Hero Redesign + Full Admin Gate (Apr 28, 2026)
- [x] **Startup Apply hero fully redesigned**: Removed orange flood gradient + white "100 Startups" badge-sticker entirely. New editorial hero uses light slate background + subtle dot-grid pattern; typographic hierarchy with "Hyderabad's Next" muted grey (context) and "100 Startups" huge black (anchor) + single orange underline accent on "100"; stat grid (₹100Cr / ₹10L / 50%) for credibility; inline partner line "Kaizer News × B The Change" (uppercase tracked); live pulsing "Applications Open · Limited to 100 seats" dot; primary "Apply Now" CTA.
- [x] **Admin auth gate extended**: Applied `require_admin` dependency to `/api/admin/reporters`, `/api/admin/reporter-news` (GET + approve + reject), and all `/api/apikeys/*` admin endpoints (via router-level dependency).
- [x] **Global axios interceptor** added to `App.js` - auto-attaches `X-Admin-Phone` header from localStorage on every request. Admin users get gated endpoints automatically; non-admin users get 403 on admin endpoints as expected.

### Phase 39 - Admin Gate + Startup Apply Polish (Apr 27, 2026)
- [x] **Admin auth gate** on `/api/admin/startup-applications`, `/export`, and `/update-status`. New dependency `auth_dep.require_admin` accepts phone via `X-Admin-Phone` header OR `?admin_phone=` query (for browser `window.open` file downloads). Matches `ADMIN_PHONE = 7386917770`. Returns 401 (missing) / 403 (wrong). `AdminStartupApplications.jsx` sends header + attaches admin_phone to CSV URL.
- [x] **Hid floating LIVE TV button** on `/startup-apply` - added `isStartupPage` check to `showFloatingLive` in `App.js`.

### Phase 38 - Startup Apply Polish + Admin Portal (Apr 27, 2026)
- [x] **Hero re-themed** - switched apply page from rose/pink gradient to pure orange/amber matching the rest of the site. Reduced "Applications Open" badge to a small uppercase pill.
- [x] **Structured Address Fields** - split single `location` into `colony` / `area` / `city` (city defaults to Hyderabad). Frontend has 3 distinct inputs with data-testids.
- [x] **Admin Startups Tab** - new `/admin` tab "Startups" backed by `<AdminStartupApplications />`. Status filter pills (All/submitted/shortlisted/interviewed/selected/rejected), search, status-update dropdown per row, detail dialog with founder profile + pitch deck/video links.
- [x] **Excel/CSV Export** - `GET /api/admin/startup-applications/export?status=...` returns UTF-8 BOM CSV with all 16 columns. Admin UI has prominent "Download Excel (CSV)" button.
- [x] **Data storage clarified** - applications stored in MongoDB collection `startup_applications`, visible in Admin → Startups tab + downloadable as Excel/CSV.

### Phase 37 - Hyderabad's Next 100 Startups Accelerator (Apr 27, 2026)
- [x] **Apply for Startup Funding** feature - joint initiative by Kaizer News & B The Change. Vision: ₹100 Crore Startup Accelerator Fund via tech development; up to ₹10L per founder.
- [x] **New Page** `/startup-apply`: Hero, program details (Who Can Apply, What You Get, What We Look For, How It Works), application form with name, mobile, email, age, location, woman-founder checkbox (50% reservation), tech business idea (≥30 chars), pitch-deck PDF upload, 1-min pitch video upload.
- [x] **Backend**: `POST /api/startup/apply`, `GET /api/startup/check/{mobile}`, `GET /api/admin/startup-applications`, `POST /api/admin/startup-applications/{id}/update-status`. Field validators for mobile (10-digit), email format, name min 2, idea min 30 chars. Duplicate-mobile guard.
- [x] **New Upload Endpoint**: `POST /api/upload/document` (PDF/DOC/DOCX, 15MB cap).
- [x] **CRITICAL FIX**: Reworked all 3 ImageKit upload endpoints (`/upload/image`, `/upload/video`, `/upload/document`) for the new imagekitio v3+ SDK API (`imagekit.files.upload(file=bytes, ...)` instead of `imagekit.upload_file(file=b64, options={...})`). Previously ALL uploads were broken; now verified working with live ImageKit URLs.
- [x] **Homepage CTA**: Added gradient "Apply for Startup Funding" button next to existing "Become a Reporter" card (`data-testid=apply-startup-cta`); routes to `/startup-apply`.

### Phase 36 - Admin Reporters Fix + Reporter Onboarding (Apr 27, 2026)
- [x] **Fixed Admin Reporters Tab (P0)**: Resolved HTTP 500 ResponseValidationError. Root cause: `parse_from_mongo` was converting str→datetime but `Reporter` model used `created_at: str`. Reversed direction (datetime→str). Pydantic v2 auto-coerces ISO strings back to datetime for datetime-typed fields, so safe for both.
- [x] **Reporter/ReporterNews Model Realignment**: Updated models to match actual frontend schema - `photo` (was `photo_url`), `location` (was `area`), `status` (was `is_approved`/`is_rejected` bools), `news_submitted`/`news_approved` counters, `bio`, `news_type`, `reporter_video_url`, `created_at`/`updated_at`.
- [x] **"Become a Citizen Reporter" Homepage CTA**: Gradient banner card visible to guest users below CategoryChips on `/`. Click navigates to `/reporter/register`.
- [x] **Profile Page Dual CTA**: Guest users see "Become a Reporter" (apply) + "Reporter Login" buttons.
- [x] **Phone validation hardening**: Added Pydantic field_validator on `/reporter/register` (10-digit regex) and `AdminReporters.jsx` retry/empty/error state with toast.

### Phase 35 - Multi-Feature Update (Apr 27, 2026)
- [x] **ePaper PDF Pixel-Perfect**: Rewrote PDF template to match web layout (Playfair Display, PT Serif, CMYK footer, correct image heights)
- [x] **Article Search**: Search bar on homepage with debounced auto-search across titles + summaries (EN + Telugu)
- [x] **Admin Changed**: 7386917770 is now admin (removed 9876543210)
- [x] **Publish Date Picker**: Admin can backdate/future-date articles from Push News form
- [x] **Exact Timestamps**: All articles show "4 Apr 2026, 2:45 PM · 23 days ago" format on cards + modal
- [x] **4-Line Minimum Rule**: Backend rejects articles with < 4 lines in description
- [x] **Auto Telugu Translation**: English articles auto-translated to Telugu, Telugu to English (both scraped and manual)
- [x] **3 AI Agents Verified**: Editor, Investigator, Social Media Expert - all producing fresh reports

### Phase 34 - ePaper PDF Layout Fix (Mar 16, 2026)
- [x] Pixel-perfect PDF with Google Fonts via @import
- [x] CMYK footer, images, proper layout

## Architecture
```
Backend: FastAPI + MongoDB + Celery + Redis
Frontend: React + Shadcn UI
AI: Gemini 2.5 Flash (via Emergent LLM Key)
Agents: Editor, Investigator, Social Media Expert, Tech Performance, 2 YouTube agents
Schedule: Scrape every 30 min → Agents auto-trigger → Telegram at 6AM/6PM IST
```

## Key Rules
- 4-line minimum description for all articles
- Auto Telugu translation for all new articles
- Admin: 7386917770 / OTP: 123456
- Production API: efficient-charisma-production-3ac3.up.railway.app

## Pending
- Backfill ~2,700 articles missing source links (P2)
- Migrate older background jobs to Celery (P2)
