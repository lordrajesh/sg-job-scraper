# Singapore Job Market Intelligence

Real-time Singapore job market dashboard aggregating 1,000+ listings from 7 sources with salary estimation, skill matching, and market analytics. Optimized for fraud/risk/analytics roles and Employment Pass eligible candidates.

**Targeted for:** Rajesh Rajagopalan — Senior Data Analyst, Fraud/Risk Analyst, Business Analyst roles (SGD 13,000+ minimum salary expectation)

> **Note:** Dashboard screenshots will be available after first deployment to Vercel and initial scrape run

## Architecture

```
Job Boards (7 sources)          Analysis Layer              Frontend
========================        ==================          ==================
LinkedIn  ─┐                    Pydantic models             Astro.js + Tailwind
Indeed    ─┤ JobSpy             3-layer dedup               Chart.js analytics
Google    ─┘                    Skill matching (0-100)      Table + Card views
JobsDB ──── GraphQL API    ──►  Salary estimation      ──►  Sticky filters
Lever ──┐                       EP eligibility              Tax calculator
Greenhouse ┤ APIs               Seniority detection         Excel export
          └──────────────────────────────────────────────────────────────────►
                                                            JSON ──► Astro ──► Vercel
                                                            GitHub Actions (daily)
```

## Features

- **7 data sources** — LinkedIn, Indeed, Google Jobs (via JobSpy), JobsDB (reverse-engineered GraphQL), Lever API, Greenhouse API
- **Salary estimation engine** — Multi-signal model calibrated from [JobsDB Singapore](https://sg.jobsdb.com/), [PayScale Singapore](https://www.payscale.com/research/SG/), and [Robert Half Singapore 2026](https://www.roberthalf.com/sg/en/insights/salary-guide). Uses seniority, company tier, role type, EP eligibility, and premium skill keywords.
- **Skill matching** — Each job scored 0-100% against a configurable skill profile (SQL, Power BI, Tableau, Python, Microsoft Azure, Scikit-Learn, XGBoost)
- **Employment Pass-Friendly detection** — Flags 50+ known international-hiring companies and visa sponsorship signals relevant to Singapore
- **Category relevance** — 12 targeted categories (Fraud Investigator, Risk Analyst, Senior Data Analyst, Business Analyst, Product/Program/Project Manager, etc.) with title-based relevance scoring
- **3-layer deduplication** — URL canonicalization + exact title/company + fuzzy matching (70% threshold)
- **134 unit tests** — Model validation, dedup logic, scoring algorithms

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Scrapers | Python 3.11, httpx (async), python-jobspy |
| Data models | Pydantic v2 with field validators |
| Analysis | Custom scoring, salary estimation, regex-based detection |
| Frontend | Astro 5, Tailwind CSS 3, Chart.js |
| Testing | pytest (134 tests) |
| Deployment | GitHub Actions, Vercel |

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt
cd frontend && npm install && cd ..

# Scrape all 12 categories (takes ~15 min)
python generate_data.py --force

# Single category test
python generate_data.py --query "fraud analyst" --location "Singapore" --force

# Run tests
python -m pytest tests/ -v

# Frontend dev server
cd frontend && npm run dev    # http://localhost:4321/sg-jobs/

# Production build + deploy
cd frontend && npm run build && cd ..
python deploy.py
```

## Data Sources

| Source | Method | Jobs | Auth |
|--------|--------|------|------|
| LinkedIn | JobSpy wrapper | ~75/query | None |
| Indeed SG | JobSpy wrapper | ~25/query | None |
| Google Jobs | JobSpy wrapper | varies | None |
| JobsDB | Reverse-engineered GraphQL | ~200/batch | None |
| Tech/Finance Companies | Lever API | ~100 SG | None |
| Finance/Tech Companies | Greenhouse API | ~80 SG | None |

## Salary Estimation

Singapore employers sometimes publish salary ranges. When not disclosed, the estimation engine uses 5 signals calibrated to SGD/month:

1. **Seniority** (Junior: SGD 4K → Director+: SGD 25K) — calibrated from Singapore market data
2. **Company tier** — FAANG/banks +30%, Big4 +20%, known SG companies +10%
3. **Role category** — Fraud/Risk roles +15-20%, Data Engineer +25%, PM roles baseline
4. **Employment Pass status** — EP-eligible companies +5%
5. **Premium skills** — ML, Cloud, Compliance: up to +15%

Confidence: High (3+ signals), Medium (1-2), Low (baseline only).

**Minimum salary target:** SGD 13,000/month (Rajesh's current: SGD 15,000)

## Project Structure

```
hk-job-scraper/
├── scrapers/           # 4 async scrapers (JobSpy, JobsDB, Lever, Greenhouse)
├── models/             # Pydantic JobListing model with validators
├── utils/              # Shared analysis (skills, salary, mandarin detection)
├── tests/              # 134 pytest tests (models, dedup, scoring)
├── frontend/           # Astro.js static site
│   └── src/components/ # Header, StatsGrid, FilterBar, JobTable, Insights, etc.
├── generate_data.py    # Main pipeline: scrape → analyze → JSON
├── merge.py            # 3-layer deduplication
├── hunter_enricher.py  # Hunter.io recruiter email enrichment
├── deploy.py           # FTP deployment to Hostinger
└── export_excel.py     # Excel report generation
```

## Author

**Rajesh Rajagopalan** — Senior Data Analyst | Fraud & Risk Analysis | Stripe & Microsoft | Singapore

- [LinkedIn](https://linkedin.com/in/rajesh-rajagopalan-72b696b9)
