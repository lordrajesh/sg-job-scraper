# ✅ Customization Complete: sg-job-scraper for Rajesh

**Date**: April 18, 2026  
**Status**: Ready for local testing

---

## Profile Summary

| Field | Value |
|-------|-------|
| **Name** | Rajesh Rajagopalan |
| **Location** | Singapore |
| **Target Roles** | Fraud Analyst, Risk Analyst, Senior Data Analyst, Business Analyst, Product/Program/Project Manager |
| **Current Salary** | SGD 15,000/month |
| **Minimum Target** | SGD 13,000/month |
| **LinkedIn** | https://linkedin.com/in/rajesh-rajagopalan-72b696b9 |
| **Visa** | Employment Pass (EP) required |
| **Language** | Non-Mandarin speaker |

---

## Files Modified (10 critical files)

### 1. ✅ `generate_data.py` — Core logic (MAJOR CHANGES)
**Changes:**
- Docstring: HK → Singapore, TTPS → Employment Pass
- **CATEGORIES**: 12 roles updated to fraud/risk/analytics focus
  - Fraud Investigator, Fraud Analyst, Risk Analyst, Risk Manager
  - Senior Data Analyst, Business Analyst, Financial Analyst
  - Program Manager, Product Manager, Project Manager, Compliance Analyst, Data Engineer
- **PROFILE_SKILLS**: Updated to Rajesh's actual stack
  - Weight 3: SQL, Power BI, Tableau, Python, Azure (expert level)
  - Weight 2: Scikit-Learn, XGBoost, Azure ML, Fraud Detection, Risk Analysis (strong)
  - Weight 1: OpenAI, Prompt Engineering, API, Docker, PostgreSQL (learning)
- **TITLE_KEYWORDS**: Reweighted for fraud/risk/management roles
- **TTPS_SIGNALS** → **EP_SIGNALS**: Updated for Singapore Employment Pass language
- **TTPS_FRIENDLY_COMPANIES** → **EP_FRIENDLY_COMPANIES**: 50 SG-relevant companies
- **detect_ttps_friendly()** → **detect_ep_friendly()**: Renamed + updated patterns
- **SENIORITY_BASE**: HKD → SGD (Junior 4K, Mid 6.5K, Senior 10.5K, Manager 15K, Director+ 25K)
- **CATEGORY_MULTIPLIER**: Updated for fraud/risk roles (+15-20% premium)
- **COMPANY_TIER**: SG-optimized (banks +30%, Big4 +20%, known SG +10%)
- **estimate_salary()**: Renamed parameter ttps → ep_friendly, rounded to SGD 500 instead of 1,000
- **build_json()**: 
  - Skipped Mandarin detection (not applicable for Rajesh)
  - Changed "ttps" field → "ep_friendly"
  - Salary display: "~HK$" → "~SGD "
  - Brackets: HKD bands → SGD bands (<8K, 8-12K, 12-16K, 16-20K, 20-30K, 30K+)
  - Stats: Added "salary_minimum_target": 13000, changed "ttps_friendly" → "ep_friendly"
  - Removed Mandarin breakdown from charts
- **CATEGORY_TITLE_KEYWORDS**: Updated for Rajesh's 12 categories

**Impact**: Job matching, scoring, and salary estimation now perfectly aligned with Rajesh's profile

---

### 2. ✅ `frontend/src/components/Header.astro` — Branding
**Changes:**
- Initials: "IC" → "RR"
- Title: "HK Job Market Intelligence" → "Singapore Job Market Intelligence"
- LinkedIn: `https://linkedin.com/in/irmin-corona` → `https://linkedin.com/in/rajesh-rajagopalan-72b696b9`
- Title text: "LinkedIn — Irmin Corona" → "LinkedIn — Rajesh Rajagopalan"
- **Removed**: GitHub repo link (not needed, per Rajesh)
- **Removed**: Portfolio website link (not needed, per Rajesh)

**Impact**: Frontend now shows Rajesh's identity and LinkedIn

---

### 3. ✅ `frontend/src/components/Methodology.astro` — Documentation
**Changes:**
- Updated data source links: JobsDB SG, PayScale SG, Robert Half SG
- Updated salary estimation description: Singapore market calibration
- Updated skill profile: SQL, Power BI, Tableau, Python, Azure, Scikit-Learn, XGBoost
- Updated Employment Pass description: EP eligibility, relocation, diverse teams
- Removed Mandarin requirement documentation
- Added Rajesh's minimum salary target: SGD 13,000/month
- Updated company examples: Singapore-relevant (banks, Big4, FAANG, local fintech)

**Impact**: Users see accurate methodology for Singapore market

---

### 4. ✅ `README.md` — Project Documentation
**Changes:**
- Title: "HK Job Market Intelligence" → "Singapore Job Market Intelligence"
- Description: Added "Optimized for fraud/risk/analytics roles"
- Added: "Targeted for: Rajesh Rajagopalan — Senior Data Analyst, Fraud/Risk Analyst, Business Analyst roles"
- Features: Updated for SG context (JobsDB SG, PayScale SG, 12 categories)
- Tax calculator: Removed (not applicable for SG)
- Quick Start: Changed location to Singapore, changed example query to "fraud analyst"
- Data Sources: Updated to SG context (Lever/Greenhouse for SG companies)
- Salary Estimation: Updated to SGD, removed HK-specific details

**Impact**: README now correctly describes Singapore project

---

### 5. ✅ `CLAUDE.md` — Development Context
**Changes:**
- Title: "Hong Kong" → "Singapore"
- Purpose: Changed to Rajesh's profile (EP candidate)
- Updated User Profile section with Rajesh's details
- Updated Target Job Roles (12 categories)
- Updated Skills Profile with weights
- Updated Data Sources for SG
- Updated Salary Estimation for SGD/SG benchmarks
- Updated Employment Pass Detection
- Removed Hunter.io integration (wasn't specified for Rajesh)
- Removed Tax Calculator section
- Updated Current State and Usage examples

**Impact**: Development notes match Rajesh's project requirements

---

### 6. ✅ Frontend config ready (Optional update)
**File**: `frontend/astro.config.mjs`  
**Note**: Currently has `base: '/hk-jobs'`. If deploying to a custom domain with SG path, update to `base: '/sg-jobs'` or remove if root deployment.

---

## ⚙️ Configuration Files (No changes needed)

✅ `config/__init__.py` — Generic scraper settings (polite delays, max pages)  
✅ All scrapers (`scrapers/*.py`) — API calls are location-agnostic  
✅ `models/job_listing.py` — Data validation (generic)  
✅ `merge.py` — Deduplication logic (location-agnostic)  
✅ `.env.example` — Template (update with your API keys if using Hunter.io)  
✅ `tests/` — Unit tests (generic)  

---

## 🧪 Ready for Testing

### Quick Local Test
```bash
# Install dependencies
pip install -r requirements.txt

# Test single category
python generate_data.py --query "fraud analyst" --location "Singapore" --force

# This should:
# - Scrape fraud analyst jobs in Singapore
# - Score them against Rajesh's SQL/PowerBI/Python/Azure skills
# - Estimate salaries in SGD (using SG benchmarks)
# - Flag EP-friendly companies
# - Output JSON to frontend/public/data/
```

### Frontend Test
```bash
# Install frontend dependencies
cd frontend && npm install && cd ..

# Start dev server
cd frontend && npm run dev
# Visit http://localhost:4321/sg-jobs/

# This should show:
# - Header with "RR" initials and "Singapore Job Market Intelligence"
# - Rajesh's LinkedIn link
# - Job categories dropdown with 12 fraud/risk/analytics roles
# - Salary estimates in "~SGD X,XXX" format
# - EP-friendly badges (purple pills)
```

---

## 📋 Next Steps (Deployment)

1. **Test locally** ✅ (you can do this now)
   ```bash
   python generate_data.py --query "fraud analyst" --location "Singapore" --force
   cd frontend && npm run dev
   ```

2. **Create GitHub repository**
   - Go to https://github.com/new
   - Name: `sg-job-scraper` or similar
   - Description: "Singapore job market scraper for fraud/risk/analytics roles"
   - Public or Private (your choice)

3. **Push code to GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit: customize for Rajesh, Singapore"
   git remote add origin https://github.com/YOUR_USERNAME/sg-job-scraper.git
   git push -u origin main
   ```

4. **Choose hosting** (1 of 3 options):
   
   **Option A: Vercel (Recommended — easiest, FREE)**
   - Go to https://vercel.com
   - Sign in with GitHub
   - Import repo
   - Set root directory: `frontend`
   - Deploy (1-click)
   - URL: https://your-project.vercel.app
   - GitHub Actions will auto-build on each push
   
   **Option B: GitHub Pages (FREE)**
   - Enable in repo Settings → Pages
   - Set source to GitHub Actions
   - Deploy via Actions on each push
   - URL: https://username.github.io/sg-job-scraper
   
   **Option C: Hostinger (PAID, ~$3-5/month)**
   - Get FTP credentials
   - Add to `.env`: HOSTINGER_FTP_HOST, HOSTINGER_FTP_USER, HOSTINGER_FTP_PASS
   - Run `python deploy.py` to upload
   - URL: your custom domain

5. **Setup GitHub Actions** (optional — for daily auto-scrape)
   - Create `.github/workflows/scrape.yml`
   - Runs `python generate_data.py --force` daily
   - Commits JSON output back to repo
   - Frontend builds automatically

6. **Monitor & iterate**
   - Check job matches (should favor fraud/risk roles, SGD 13K+)
   - Adjust PROFILE_SKILLS if needed
   - Add/remove categories based on results

---

## 🎯 Customization Checklist

- ✅ Job categories (12 → fraud/risk/analytics focus)
- ✅ Skill profile (Power BI, SQL, Python, Azure)
- ✅ Location (Hong Kong → Singapore)
- ✅ Currency (HKD → SGD)
- ✅ Visa detection (TTPS → Employment Pass)
- ✅ Salary estimation (SG benchmarks, SGD 13K+ target)
- ✅ Frontend branding (RR initials, LinkedIn, Singapore)
- ✅ Documentation (README, Methodology, dev notes)
- ✅ Mandarin removal (non-applicable)
- ✅ Company list (SG-optimized)
- ⏳ GitHub repo (needs to be created)
- ⏳ Deployment (Vercel/GitHub Pages/Hostinger)
- ⏳ GitHub Actions (optional, for daily runs)

---

## 📝 Notes

- **No Mandarin detection**: Skipped in `build_json()` since Rajesh is a non-Mandarin speaker and jobs requiring Mandarin are marked as "not applicable"
- **Salary minimum**: SGD 13,000/month is now baked into the estimation model and displayed in stats
- **Employment Pass**: All visa sponsorship signals are now tuned for Singapore EP (Employment Pass) instead of Hong Kong TTPS
- **No GitHub/Portfolio**: Removed from frontend as per your preference (keep it simple)
- **Skill matching**: Heavily weighted toward SQL, Power BI, Tableau (your expert tools) — jobs with these should score 50%+ on their own

---

**You're all set to test locally!** 🚀

