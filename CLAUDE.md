# Singapore Job Scraper

## Project
- **Live URL**: TBD (planned: personal domain or GitHub Pages)
- **GitHub**: TBD — needs repo created and pushed
- **Hosting**: Vercel (free) or Hostinger (paid)
- **Architecture**: Astro.js static frontend + Python scrapers + GitHub Actions
- **Purpose**: Personal job hunting tool for Employment Pass eligible candidates (Rajesh Rajagopalan)

## User Profile
- **Name**: Rajesh Rajagopalan
- **LinkedIn**: https://linkedin.com/in/rajesh-rajagopalan-72b696b9
- **Current salary**: SGD 15,000/month
- **Minimum target**: SGD 13,000/month
- **Location**: Singapore (non-Mandarin speaker)
- **Visa**: Employment Pass (EP) required

## Target Job Roles (12 categories, priority order)
**Tier 1 (core fraud/risk/compliance):**
- Fraud Investigator, Fraud Analyst, Risk Analyst, Risk Manager

**Tier 2 (data/business analysis):**
- Senior Data Analyst, Business Analyst, Financial Analyst

**Tier 3 (management/adjacent):**
- Program Manager, Product Manager, Project Manager, Compliance Analyst, Data Engineer

## Skills Profile
**Weight 3 (Expert):** SQL, Power BI, Tableau, Python, Microsoft Azure, Data Analysis, Reporting, Dashboard, Visualization, Analytics

**Weight 2 (Strong):** Scikit-Learn, XGBoost, Machine Learning, Azure ML, Azure Synapse, Cosmos DB, Fraud Detection, Risk Analysis, Compliance, AML, KYC, Excel, MS Office

**Weight 1 (Learning):** OpenAI, Prompt Engineering, GPT, API, Git, Docker, Agile, AWS, GCP, PostgreSQL, Jira, Power Automate

## Frontend (Astro.js)
- Located in `frontend/` — Astro 5 + Tailwind CSS 3
- **Theme**: Orange/black
- `base: '/sg-jobs'` in astro.config.mjs
- **Layout order**: Header → Stats → Sticky FilterBar → Skill Tags → Job Table → Insights (collapsed) → Methodology (collapsed)
- Components: Header, StatsGrid, FilterBar, SkillTags, JobTable (desktop table + mobile cards), Insights, Methodology, Footer
- **Match score**: colored progress bar per job (green ≥50%, orange ≥25%, gray <25%)
- **EP-Friendly badges**: purple pill on jobs from known international-hiring companies
- **Filters**: text search, seniority, work mode, source, EP-only checkbox
- Client-side: Chart.js (3 charts), XLSX.js for Excel export

## Data Sources (5 working)
- **JobSpy** — wraps LinkedIn + Indeed + Google Jobs
- **JobsDB GraphQL** — `sg.jobsdb.com/graphql`, full descriptions
- **Lever API** — company career pages (tech/finance companies in SG)
- **Greenhouse API** — company career pages (finance/tech companies in SG)
- **Indeed SG** — via JobSpy

## Salary Estimation (SGD/month)
- Calibrated from JobsDB SG, PayScale SG, Robert Half SG 2026
- Base seniority: Junior SGD 4K → Director+ SGD 25K
- Role multiplier: Fraud/Risk +15-20%, Data Engineer +25%, PM baseline
- Company tier: FAANG/banks +30%, Big4 +20%, known SG +10%
- Premium skills: +15% max
- **Confidence**: High (3+ signals), Medium (1-2), Low (baseline)

## Employment Pass Detection
- Company name matched against ~50 known MNCs (banks, Big4, FAANG, SG tech)
- Description regex for visa/sponsorship/relocation/diverse team signals
- Seniority detection: Junior/Mid/Senior/Manager/Director+ from title
- Work mode: Remote/Hybrid/On-site from description

## Current State (April 2026)
- **generate_data.py**: Updated with Rajesh's profile, Singapore salary, 12 categories
- **Header.astro**: Updated initials (RR), location (Singapore), LinkedIn URL
- **Methodology.astro**: Updated salary benchmarks, skill profile, EP references
- **README.md**: Updated for Singapore context
- **Pending**: Test locally, configure GitHub repo, enable GitHub Actions, deploy

## Usage
```bash
# Full scrape (all 12 categories)
python generate_data.py --force

# Single category test
python generate_data.py --query "fraud analyst" --location "Singapore" --force

# Frontend dev
cd frontend && npm run dev    # http://localhost:4321/sg-jobs/

# Production build
cd frontend && npm run build && cd ..
```
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
