# API & Services Reference

## Required APIs (Already Integrated — No Signup Needed)

### 1. **python-jobspy** — FREE
- **Purpose**: Scrape LinkedIn, Indeed, Google Jobs
- **Auth**: None
- **Cost**: Free (rate-limited but sufficient)
- **Setup**: `pip install python-jobspy` (already in `requirements.txt`)
- **Usage**: `JobSpyScraper` class in `scrapers/jobspy_scraper.py`

### 2. **JobsDB GraphQL API** — FREE
- **Purpose**: Singapore job listings (local DB with full descriptions)
- **Auth**: None (public endpoint)
- **Cost**: Free
- **Endpoint**: `https://sg.jobsdb.com/graphql`
- **Usage**: `JobsDBScraper` class in `scrapers/jobsdb.py`
- **Note**: Reverse-engineered; may change if JobsDB updates

### 3. **Lever API** — FREE
- **Purpose**: Company career pages (Stripe, Microsoft, Google, etc.)
- **Auth**: None (public endpoint)
- **Cost**: Free
- **Endpoint**: `https://api.lever.co/v0/postings/{company}`
- **Usage**: `LeverScraper` class in `scrapers/lever.py`
- **Coverage**: ~150+ Singapore jobs from known companies

### 4. **Greenhouse API** — FREE
- **Purpose**: Company career pages (tech & finance leaders)
- **Auth**: None (public endpoint)
- **Cost**: Free
- **Endpoint**: `https://boards.greenhouse.io/api/v1/boards/{board_token}/jobs`
- **Usage**: `GreenhouseScraper` class in `scrapers/greenhouse.py`
- **Coverage**: ~150+ Singapore jobs from known companies

---

## Optional APIs (Recommended Features)

### 5. **Hunter.io** — PAID ($99+/month) [OPTIONAL]
- **Purpose**: Find & verify recruiter emails at target companies
- **When to use**: Advanced job hunting (reach out to recruiters directly)
- **Cost**: $99+/month (1,660 credits/month)
- **Signup**: https://hunter.io/pricing
- **Usage**: `hunter_enricher.py` (optional integration)
- **Auth**: Add `HUNTER_API_KEY` to `.env`
- **Current Status**: Not actively used in daily workflow (optional feature)

### 6. **GitHub Actions** — FREE
- **Purpose**: Automatic daily job scraping & website refresh
- **When to use**: Always (keep dashboard updated daily)
- **Cost**: Free for public repos, ~$0.008/min for private
- **Setup**: 
  1. Create `.github/workflows/scrape.yml`
  2. Configure cron schedule (e.g., `0 9 * * *` = 9 AM daily)
  3. Add GitHub secrets for any API keys
- **Current Status**: Ready to configure (examples in `CLAUDE.md`)

### 7. **Web Hosting & Deployment** — FREE or PAID

#### Option A: **Vercel** (RECOMMENDED) ✅
- **Cost**: Free tier available
- **Signup**: https://vercel.com
- **Setup**: 
  1. Create account (GitHub login recommended)
  2. Import `lordrajesh/sg-job-scraper` from GitHub
  3. Set root directory: `./frontend`
  4. Create GitHub secrets: VERCEL_TOKEN, VERCEL_ORG_ID, VERCEL_PROJECT_ID
  5. GitHub Actions automatically deploys on git push
- **Benefit**: Zero-config Astro deployment, instant preview URLs, automatic daily builds
- **Best for**: Our current setup (automatic daily scraping + deployment)
- **Current Status**: Configured in GitHub Actions workflow

#### Option B: **GitHub Pages** (FREE)
- **Cost**: Free
- **Setup**:
  1. Push `frontend/dist/` to `gh-pages` branch
  2. Enable Pages in repo settings
  3. URL: `https://lordrajesh.github.io/sg-job-scraper/`
- **Benefit**: No server needed, integrated with GitHub
- **Downside**: Slower custom domain setup

#### Option C: **Netlify** (FREE + Paid)
- **Cost**: Free tier available
- **Setup**: Similar to Vercel (import repo, auto-deploy)
- **Benefit**: Easy environment variable management

---

## Services to Integrate (For Enhanced Features)

### 8. **Google Analytics** — FREE
- **Purpose**: Track visitor behavior, job search trends
- **When to use**: After deployment, to measure engagement
- **Signup**: https://analytics.google.com/
- **Implementation**: Add GA4 tag to `Layout.astro`
- **Current Status**: Not integrated yet

### 9. **LinkedIn** — BUSINESS PROFILE
- **Purpose**: Social sharing, SEO
- **When to use**: Brand your scraper, share insights
- **Current Status**: Header links to LinkedIn profile (update URL)

### 10. **GitHub Repository** — FREE
- **Purpose**: Version control, Actions automation
- **Signup**: https://github.com
- **Current Status**: Ready (update repo name to Rajesh's)

---

## Authentication & Credentials Checklist

### Must Configure in `.env`

```bash
# Scraper settings (optional, defaults are fine)
MIN_DELAY=2
MAX_DELAY=5
MAX_PAGES=5

# Hunter.io (optional — only if using email enrichment)
HUNTER_API_KEY=your_key_here

# Hostinger FTP (optional — only if hosting on Hostinger)
HOSTINGER_FTP_HOST=your.hostinger.com
HOSTINGER_FTP_USER=your_username
HOSTINGER_FTP_PASS=your_password
HOSTINGER_FTP_DIR=/public_html/hk-jobs/
```

### GitHub Secrets (For GitHub Actions)

If using GitHub Actions for auto-deployment, add these secrets:

```
HOSTINGER_FTP_HOST
HOSTINGER_FTP_USER
HOSTINGER_FTP_PASS
HUNTER_API_KEY (optional)
```

**How to add**: GitHub repo → Settings → Secrets and variables → Actions

---

## Signup Priority

### Tier 1 — MANDATORY
- ✅ **python-jobspy** (pip install) — Required for scraping
- ✅ **GitHub account** — Required for code storage
- ✅ **Python environment** — Required to run locally

### Tier 2 — STRONGLY RECOMMENDED
- 🔶 **Hosting** (Hostinger / Vercel / GitHub Pages) — Without this, site won't be live
  - **Pick one**: Vercel (easiest, 5 min setup)

### Tier 3 — NICE TO HAVE
- 🟡 **Hunter.io** ($99/month) — Advanced recruiter outreach
- 🟡 **GitHub Actions** (free) — Automatic daily updates
- 🟡 **Google Analytics** (free) — Understand visitor behavior

### Tier 4 — BONUS
- ⚪ **LinkedIn** — Update profile links
- ⚪ **Custom domain** — Brand it as your own job board

---

## Recommended Quick Start Path

```
1. Keep all required APIs as-is (no signup needed)
2. Create GitHub account (if not already)
3. Update job categories & skills in generate_data.py
4. Test locally: python generate_data.py
5. Deploy to Vercel (takes 5 min)
6. (Optional) Setup Hunter.io later if recruiting outreach needed
7. (Optional) Enable GitHub Actions for daily updates
```

---

## Cost Summary

| Service | Tier | Cost | Required |
|---------|------|------|----------|
| python-jobspy | Free | $0 | ✅ Yes |
| JobsDB API | Free | $0 | ✅ Yes |
| GitHub | Free | $0 | ✅ Yes |
| Vercel / Netlify | Free | $0 | ⚠️ Hosting needed |
| Hunter.io | Starter | $99/month | ❌ Optional |
| Hostinger | Shared | $3-12/month | ❌ Optional (if not using Vercel) |
| Google Analytics | Free | $0 | ❌ Optional |
| **TOTAL (Minimal)** | | **$0-3/month** | |
| **TOTAL (Full Featured)** | | **~$100-115/month** | |

**Most affordable**: $0/month using GitHub Actions + Vercel + free APIs

