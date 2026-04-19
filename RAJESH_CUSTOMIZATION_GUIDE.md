# Customization Guide: Making sg-job-scraper for Rajesh

## Phase 1: Profile Definition (Do This First)

Before touching code, define Rajesh's profile:

1. **Target Location(s)**: Hong Kong, Singapore, elsewhere?
2. **Core Skills** (Weight 3 — Expert):
   - Current example: power bi, sql, python, excel, seo, fraud, reporting, dashboard
   - **Rajesh**: ?
3. **Strong Skills** (Weight 2):
   - Current example: php, mysql, javascript, wordpress, snowflake
   - **Rajesh**: ?
4. **Learning Skills** (Weight 1):
   - Current example: machine learning, docker, git, react, dbt
   - **Rajesh**: ?
5. **Target Job Categories** (12 recommended):
   - Current for Irmin: Data Analyst, Web Dev, SEO, BI, Fraud/Risk, etc.
   - **Rajesh**: ?
6. **Career Focus**: Visa sponsorship priority? Salary range? Industry preference?

---

## Phase 2: Code Modifications

### A. Core Skill Profile Configuration

**File**: [generate_data.py](generate_data.py) (lines 29-103)

**Changes needed:**

1. **Replace CATEGORIES dict** (lines 29-57)
   - Change 12 category keys, labels, and search queries
   - Each category should have 2-4 relevant search queries
   - Example:
     ```python
     "django-backend": {
         "label": "Django Developer",
         "queries": ["django developer", "python backend", "django rest api"],
     },
     ```

2. **Replace PROFILE_SKILLS dict** (lines 62-103)
   - Replace all skills with Rajesh's actual stack
   - Keep same weight structure: 3=expert, 2=strong, 1=learning
   - Example:
     ```python
     PROFILE_SKILLS = {
         # Weight 3
         "django": 3, "python": 3, "javascript": 3, "react": 3,
         # Weight 2
         "postgresql": 2, "docker": 2, "git": 2,
         # Weight 1
         "kubernetes": 1, "aws": 1,
     }
     ```

3. **Update calc_skill_match() function** (lines 139-186)
   - Modify TITLE_KEYWORDS dict to match Rajesh's roles
   - Current example maps job titles to relevance points
   - Adjust thresholds if needed

4. **Update TTPS_FRIENDLY_COMPANIES set** (lines 203-231)
   - Keep as-is unless Rajesh's visa needs are different
   - Can trim companies irrelevant to Rajesh's target roles

### B. Frontend Text Changes

**File**: [frontend/src/components/Header.astro](frontend/src/components/Header.astro)

**Changes needed:**

1. **Line 5**: Change initials
   ```astro
   <div class="w-9 h-9 rounded-lg bg-white/15 flex items-center justify-center text-white font-bold text-sm shrink-0">IC</div>
   ```
   Replace `IC` with Rajesh's initials (e.g., `RR`)

2. **Line 7**: Keep or change title
   ```astro
   <h1 class="text-base sm:text-lg font-bold text-white tracking-tight leading-tight">HK Job Market Intelligence</h1>
   ```
   Can change to `SG Job Market Intelligence` or `Asia Job Market Intelligence` depending on location

3. **Lines 20-21**: Update LinkedIn URL
   ```astro
   <a href="https://linkedin.com/in/irmin-corona" target="_blank" rel="noopener"
     class="w-7 h-7 rounded-md bg-white/10 hover:bg-white/20 flex items-center justify-center transition" title="LinkedIn — Irmin Corona">
   ```
   Replace with Rajesh's LinkedIn profile URL and name

4. **Line 29**: Update GitHub repo URL
   ```astro
   <a href="https://github.com/ircorona/hk-job-scraper" target="_blank" rel="noopener"
   ```
   Replace with your actual repo path

5. **Line 35**: Update portfolio/blog URL
   ```astro
   <a href="https://climbthesearches.com" target="_blank" rel="noopener"
   ```
   Replace with Rajesh's portfolio URL (or remove if none)

### C. Frontend Data & Descriptions

**File**: [frontend/src/components/Methodology.astro](frontend/src/components/Methodology.astro) (lines 12-34)

**Changes needed:**

1. **Update salary benchmark links** (lines 14-16)
   - If targeting Singapore: use SG salary sites
   - If Hong Kong: keep as-is or update to current year
   - Example: Replace JobsDB HK link with Singapore equivalent

2. **Update Match Score description** (line 20)
   - Change "Power BI, SQL, Python, fraud detection, technical SEO" to Rajesh's actual skills

3. **Optional**: Update TTPS description if visa sponsorship is not a concern

### D. Resume / Contact Info

**File**: [resume/templates/rendercv_reference.md](resume/templates/rendercv_reference.md)

**Changes needed:**

1. **Line 10**: Name
   ```yaml
   name: "Irmin Corona"
   ```

2. **Lines 15, 18**: Website and LinkedIn
   ```yaml
   website: "https://climbthesearches.com"
   ...
   username: irmin-corona
   ```

### E. Config Files

**File**: [config/__init__.py](config/__init__.py)

**No changes needed** — these are generic scraper settings
- MIN_DELAY, MAX_DELAY: polite delays (keep as-is)
- MAX_PAGES: number of pages to scrape per source
- OUTPUT_FORMAT: csv or json

**File**: [.env.example](.env.example) (if exists)

**Changes needed:**

- Add any new API keys for Rajesh's setup
- If using Hunter.io, add HUNTER_API_KEY

---

## Phase 3: API/Services Setup

### Essential APIs (Free/Public)

| API | Purpose | Auth | Cost | Sign-up |
|-----|---------|------|------|---------|
| **JobSpy** | LinkedIn, Indeed, Google Jobs | None | Free | `pip install python-jobspy` |
| **JobsDB GraphQL** | Hong Kong job listings | None | Free | No signup needed |
| **Lever API** | Company career pages | None | Free | Public endpoint |
| **Greenhouse API** | Company career pages | None | Free | Public endpoint |

**Action**: No signup needed for these. They're already integrated.

### Optional APIs

| API | Purpose | When Needed | Cost | Sign-up |
|-----|---------|-------------|------|---------|
| **Hunter.io** | Email enrichment (find recruiter contacts) | Advanced networking | $99+/month | https://hunter.io/pricing |
| **GitHub Actions** | Daily scheduled scraping | Auto-refresh dashboard | Free (public repo) | Built-in to GitHub |
| **Hostinger FTP** | Web hosting | Deploy frontend | $2.99-12/month | https://www.hostinger.com |

**Action**: Only if Rajesh wants email enrichment or automatic daily updates.

---

## Phase 4: Location-Specific Changes

### If Target = Hong Kong (Current)
- ✅ Keep all scrapers as-is
- Keep salary estimation (HKD currency)
- Keep TTPS detection (Hong Kong Work Visa)
- No changes needed

### If Target = Singapore
1. **Update frontend title**: `SG Job Market Intelligence`
2. **Update salary sites**: Replace HK JobsDB links with:
   - https://sg.jobsdb.com/
   - https://www.payscale.com/research/SG/
   - Singapore MOM salary data
3. **Update salary currency**: HKD → SGD
4. **Update tax calculator**: Remove HK IRD tax calculator, add Singapore tax
5. **Modify salary estimation**: Adjust salary brackets for Singapore market
6. **Keep TTPS logic**: Singapore has similar visa sponsorship requirements

### If Target = Multiple Locations
1. Create separate category folders: `data/hk/`, `data/sg/`, `data/asia/`
2. Modify `generate_data.py` to loop over locations
3. Update filter UI to include location selector
4. Build separate salary estimation models per location

---

## Phase 5: File Change Summary

### High Priority (Must Change)

| File | Change | Impact |
|------|--------|--------|
| [generate_data.py](generate_data.py) | CATEGORIES, PROFILE_SKILLS, TITLE_KEYWORDS, TTPS_FRIENDLY_COMPANIES | Skills matching, job relevance |
| [frontend/src/components/Header.astro](frontend/src/components/Header.astro) | Initials, LinkedIn, GitHub, website URLs | Branding & credit |
| [frontend/src/components/Methodology.astro](frontend/src/components/Methodology.astro) | Skill profile description | Documentation accuracy |

### Medium Priority (Should Change)

| File | Change | Impact |
|------|--------|--------|
| [README.md](README.md) | Update project description | Documentation |
| [resume/templates/rendercv_reference.md](resume/templates/rendercv_reference.md) | Name, LinkedIn, website | Resume/CV |
| [CLAUDE.md](CLAUDE.md) | Change "Irmin Corona" to "Rajesh", update categories, skills, hiring profile | Development context |

### Low Priority (Nice to Have)

| File | Change | Impact |
|------|--------|--------|
| [models/job_listing.py](models/job_listing.py) | Field validators for new languages (e.g., Hindi, Tamil) | Data quality |
| [frontend/src/components/TaxCalculator.astro](frontend/src/components/TaxCalculator.astro) | Update tax rates if different location | Tax accuracy |

---

## Phase 6: Deployment Setup

### GitHub
1. Create/update repo: `github.com/rajesh/sg-job-scraper` (or similar)
2. Add `.env` file (git-ignored) with API keys
3. Set up GitHub Actions:
   - Trigger: Daily at 9 AM local time
   - Action: Run `python generate_data.py --force`
   - Push output to `frontend/public/data/`

### Hosting

**Option A: Hostinger (Recommended for continuity)**
- FTP credentials in `.env` as HOSTINGER_FTP_HOST, HOSTINGER_FTP_USER, HOSTINGER_FTP_PASS
- Deploy via [deploy.py](deploy.py)
- Cost: ~$3-5/month

**Option B: GitHub Pages (Free)**
- No FTP needed
- Slightly more setup
- Cost: Free

**Option C: Vercel (Free + Paid)**
- Simple Astro deployment
- Auto-deploys on git push
- Cost: Free tier available

---

## Quick Start Checklist

- [ ] Define Rajesh's profile (skills, categories, location)
- [ ] Update [generate_data.py](generate_data.py) CATEGORIES
- [ ] Update [generate_data.py](generate_data.py) PROFILE_SKILLS
- [ ] Update [generate_data.py](generate_data.py) TITLE_KEYWORDS
- [ ] Update Header.astro (name, LinkedIn, website)
- [ ] Update Methodology.astro (skill description)
- [ ] Test locally: `python generate_data.py --query "test query"`
- [ ] Test frontend: `cd frontend && npm run dev`
- [ ] Set up GitHub repo
- [ ] Set up Hostinger FTP (or alternative hosting)
- [ ] Configure GitHub Actions for daily runs
- [ ] Deploy frontend
- [ ] Test live site

---

## Questions to Answer Before Starting

1. **Rajesh's top 5 skills?** (exact names as they appear in job descriptions)
2. **Target job titles?** (e.g., "Django Developer", "Full Stack", "Backend Engineer")
3. **Location preference?** (Hong Kong, Singapore, multiple?)
4. **Visa sponsorship needed?** (affects TTPS logic)
5. **Salary expectations?** (for baseline estimation)
6. **Portfolio URL?** (for Header links)
7. **LinkedIn profile URL?**
8. **GitHub repo name?**
9. **Hosting preference?** (Hostinger, GitHub Pages, Vercel, etc.)
10. **Website domain?** (e.g., climbthesearches.com/rajesh-jobs/)

