# Hong Kong Job Scraper

## Project
- **Live URL**: TBD (planned: climbthesearches.com/hk-jobs/)
- **GitHub**: TBD — needs repo `ircorona/hk-job-scraper` created, then push
- **Hosting**: Hostinger shared hosting (same as Mexico scraper)
- **Architecture**: Astro.js static frontend + Python scrapers + Hunter.io enrichment + GitHub Actions
- **Purpose**: Personal job hunting tool + portfolio piece for TTPS visa holder (Irmin Corona)

## Frontend (Astro.js) — Redesigned March 29
- Located in `frontend/` — Astro 5 + Tailwind CSS 3
- **Theme**: Orange/black (matches climbthesearches.com brand)
- `base: '/hk-jobs'` in astro.config.mjs
- **Layout order** (jobs-first hierarchy): Header → Stats → Sticky FilterBar → Skill Tags → Job Table → Insights (collapsed) → Tax Calculator (collapsed) → Methodology (collapsed)
- Components: Header, StatsGrid, FilterBar, SkillTags, JobTable (desktop table + mobile cards), Insights (3 charts), TaxCalculator, Methodology, Footer
- **Match score**: colored progress bar per job (green ≥50%, orange ≥25%, gray <25%)
- **TTPS badges**: purple pill on jobs from known international-hiring companies
- **Filters**: text search, seniority, work mode, source, TTPS-only checkbox
- **Sort indicators**: ↑↓ arrows on active column, default sort by match score
- Client-side: Chart.js (3 charts only), XLSX.js for Excel export
- SEO: JSON-LD (WebApplication), OG tags, canonical URL

## Data Sources (5 working)
- **JobSpy** — wraps LinkedIn + Indeed + Google Jobs, no API keys
- **JobsDB GraphQL** — reverse-engineered `hk.jobsdb.com/graphql`, HK zone = `asia-1`, full descriptions
- **Binance (Lever API)** — `api.lever.co/v0/postings/binance?location=Hong%20Kong` — **138 HK jobs**, no auth, full descriptions, work type, team, apply URLs
- **LinkedIn** (via JobSpy) — rate-limits after page 10 without proxies
- **Indeed HK** (via JobSpy) — `country_indeed="Hong Kong"`

## Sources that DON'T work
- **Adzuna HK**: Country code `hk` returns 404
- **JobsDB HTML**: Cloudflare blocks httpx
- **Indeed HK HTML**: Returns 403
- **CTgoodjobs**: SPA with no API

## Categories (12, targeted for Irmin's profile)
Each category has 2-4 search queries for broader coverage:
- **Tier 1 (core)**: Data Analyst, Business Intelligence, Fraud & Risk Analyst, Analytics Manager
- **Tier 2 (secondary)**: Web Developer, Full Stack Developer, SEO & Digital Marketing (incl. "technical SEO")
- **Tier 3 (adjacent)**: Data Engineer, Product Analyst, Python & Automation, AI & Data Science, Fintech

## Skill Match Scoring
- Each job scored 0-100% against Irmin's actual stack
- **Title keywords** (up to 25 pts): "data analyst"=25, "power bi"=25, "technical seo"=25, "web developer"=20, etc.
- **Description skills** (up to 75 pts): weighted by proficiency — power bi/sql/python/excel/seo=3, php/mysql/javascript/wordpress=2, machine learning/docker/react=1
- Kubernetes, DevOps, Terraform, deep infra excluded (not competitive for these)

## TTPS-Friendly Detection
- Company name matched against ~60 known MNCs (HSBC, Deloitte, Binance, Google, etc.)
- Description regex for visa/sponsorship/relocation/diverse team signals
- Work mode detection: remote/hybrid/on-site from description keywords
- Seniority detection: Junior/Mid/Senior/Manager/Director+ from title

## Hunter.io Integration
- **API key**: in `.env` as HUNTER_API_KEY (also needs GitHub Secret)
- **Plan**: Starter — 1,660 searches remaining, 3,320 verifications remaining
- **Enricher**: `hunter_enricher.py` — domain-search → score contacts by recruiter relevance → verify top emails
- **Binance test**: Found Alexandru Ene, Director of Human Resources (99% confidence, verified deliverable)
- **Strategy**: Only enrich companies with match≥25% jobs at Mid/Senior/Manager level — 22 companies identified, 22 credits needed (1.3% of budget)

## Hunter.io Enrichment Hit List (pending — do tomorrow)
**Tier 1 (direct employers, enrich first):**
Binance (done), OKX, Bybit, Lalamove [TTPS], Bank of China HK, China CITIC Bank [TTPS], Agoda, Dentsu HK, Bending Spoons

**Tier 2 (recruiters):**
Michael Page, Hays, Gravitas Recruitment

**Skip:** TELUS Digital (data labeling), Dwarsrivier (wrong geo), FedEx/Manulife (internships)

## Tax Calculator — Verified March 29
- **2025/26 IRD rates** confirmed correct: progressive bands (2/6/10/14/17%), basic allowance HK$132,000
- **MPF added**: 5% capped at HK$1,500/mo, tax-deductible up to HK$18,000/yr
- **Two-tier standard rate**: 15% on first $5M, 16% on remainder
- Sources: gov.hk, mpfa.org.hk, PwC tax summaries

## Current State (March 29, 2026)
- **1,955 jobs scraped** across 12 categories, 707 unique after dedup
- **152 TTPS-friendly** jobs identified
- **38 strong matches** (match≥25%, Mid/Senior/Manager seniority)
- **Binance**: 138 HK jobs via Lever API, 11 are strong matches (top: 53% Data Analyst)
- Frontend redesigned: orange/black theme, jobs-first layout, mobile cards, sticky filters
- Tax calculator verified with MPF
- Hunter.io tested and working (Binance HR Director found + verified)
- GitHub Actions workflow ready (scrape → Hunter enrich → Astro build → FTP deploy)
- **Pending**: Create GitHub repo, push code, configure secrets, run first workflow

## Usage
```bash
# Full scrape (all 12 categories, 5 sources)
python generate_data.py --force

# Single category test
python generate_data.py --query "data analyst" --location "Hong Kong" --force

# Hunter.io
python hunter_enricher.py --check-credits
python hunter_enricher.py --company "Binance" --verify-top
python hunter_enricher.py --max 12          # enrich top 12 companies

# Frontend
cd frontend && npm run dev                  # local: http://localhost:4321/hk-jobs/
cd frontend && npm run build                # production build → dist/
```

## FTP deploy — critical notes
- Hostinger uses **explicit FTPS** (AUTH TLS on port 21), NOT implicit FTPS (port 990)
- **NEVER use `ftps://`** — it attempts implicit FTPS and will fail silently
- **NEVER use `lftp`** — it does not work with Hostinger regardless of settings
- **NEVER use `SamKirkland/FTP-Deploy-Action`** — intermittent timeouts due to no keepalive
- **ALWAYS use `curl --ssl-reqd --insecure`** with `ftp://` — this is the only method proven to work
- Use `--ftp-create-dirs` when uploading Astro build (nested directory structure)

## Credentials & Secrets Needed
All credentials stored in `.env` (gitignored) and GitHub Secrets:
- `FTP_HOST` — Hostinger FTP server IP
- `FTP_USER` — Hostinger FTP username
- `FTP_PASS` — Hostinger FTP password
- `HUNTER_API_KEY` — Hunter.io API key
