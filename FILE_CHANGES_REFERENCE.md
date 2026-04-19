# File Modification Reference (At-a-Glance)

## Files That Need Changes

### 1. `generate_data.py` — HIGHEST PRIORITY

**Lines 29-57: CATEGORIES (12 job categories)**
```python
CATEGORIES = {
    "data-analyst": {
        "label": "Data Analyst",                          # ← Change label
        "queries": ["data analyst", "reporting analyst"], # ← Change search queries
    },
    # ... repeat for 12 categories
}
```
**Change**: Replace all 12 categories with Rajesh's target roles + search queries

---

**Lines 62-103: PROFILE_SKILLS (Skill matching weights)**
```python
PROFILE_SKILLS = {
    # Weight 3 — expert level
    "power bi": 3, "sql": 3, "python": 3,      # ← CHANGE THESE
    # Weight 2 — strong
    "php": 2, "mysql": 2,                      # ← CHANGE THESE
    # Weight 1 — familiar
    "docker": 1, "git": 1,                     # ← CHANGE THESE
}
```
**Change**: Replace all skills with Rajesh's actual stack (keep weights)

---

**Lines 139-186: TITLE_KEYWORDS (Title relevance scoring)**
```python
TITLE_KEYWORDS = {
    "data analyst": 25, "power bi": 25,        # ← CHANGE THESE
    "web developer": 20, "seo": 20,            # ← CHANGE THESE
    # ...
}
```
**Change**: Replace job titles with Rajesh's target roles

---

**Lines 203-231: TTPS_FRIENDLY_COMPANIES (International-hiring companies)**
```python
TTPS_FRIENDLY_COMPANIES = {
    "hsbc", "google", "microsoft",             # ← KEEP OR TRIM
    # ... 60+ company names
}
```
**Change**: Optional — keep as-is unless irrelevant to Rajesh's targets

---

### 2. `frontend/src/components/Header.astro` — HIGH PRIORITY

**Line 5: Replace initials**
```astro
<div class="w-9 h-9 ...">IC</div>  <!-- Change IC to RR or other -->
```
**Change**: Replace "IC" with Rajesh's initials

---

**Line 7: Optional title change**
```astro
<h1>HK Job Market Intelligence</h1>  <!-- Can change to SG or other location -->
```
**Change**: Optional — update location name if not Hong Kong

---

**Line 20: LinkedIn profile**
```astro
<a href="https://linkedin.com/in/irmin-corona" title="LinkedIn — Irmin Corona">
```
**Change**: Replace URL and name with Rajesh's LinkedIn

---

**Line 29: GitHub repo**
```astro
<a href="https://github.com/ircorona/hk-job-scraper">
```
**Change**: Replace with Rajesh's GitHub repo

---

**Line 35: Portfolio website**
```astro
<a href="https://climbthesearches.com">
```
**Change**: Replace with Rajesh's website or remove

---

### 3. `frontend/src/components/Methodology.astro` — MEDIUM PRIORITY

**Line 20: Update Match Score description**
```astro
<p>...Match score: Measures alignment with a specific skill profile: Power BI, SQL, Python, fraud detection, technical SEO...</p>
```
**Change**: Replace the skill list with Rajesh's actual profile skills

---

**Lines 14-16: Salary benchmark links (Optional)**
```astro
<a href="https://hk.jobsdb.com/career-advice/role/data-analyst/salary">JobsDB salary medians</a>
```
**Change**: Update if targeting different location (Singapore, etc.)

---

### 4. `resume/templates/rendercv_reference.md` — LOW PRIORITY

**Line 10: Name**
```yaml
name: "Irmin Corona"  # ← Change to "Rajesh ..."
```

**Line 15: Website**
```yaml
website: "https://climbthesearches.com"  # ← Change to Rajesh's
```

**Line 18: LinkedIn**
```yaml
username: irmin-corona  # ← Change to Rajesh's
```

---

### 5. `README.md` — LOW PRIORITY

**Lines mentioning Irmin's profile (search for "Irmin")**
- Update description to focus on Rajesh's use case
- Update "Targeted for TTPS visa holder profile" if different

---

### 6. `CLAUDE.md` — LOW PRIORITY

**Line mentioning "Purpose: Personal job hunting tool for TTPS visa holder (Irmin Corona)"**
- Update to Rajesh's name and visa needs

---

## Files That DO NOT Need Changes

✅ **Safe to leave as-is:**
- `main.py` — Generic scraper
- `merge.py` — Deduplication logic (location-agnostic)
- `export_excel.py` — Excel export (generic)
- `deploy.py` — FTP deployment (just needs .env config)
- `hunter_enricher.py` — Email enrichment (optional feature)
- All scrapers in `scrapers/` — API calls (generic)
- `models/job_listing.py` — Data validation (generic)
- `tests/` — Unit tests (generic)
- `frontend/src/pages/index.astro` — Job table rendering (generic)
- `frontend/src/components/JobTable.astro` — Table layout (generic)
- `frontend/src/components/FilterBar.astro` — Filter UI (generic)
- `frontend/src/components/TaxCalculator.astro` — Only change tax rates if location differs
- `config/` — Global config (optional tweaks)

---

## Environment Configuration (`.env`)

**Create/update `.env` file:**
```bash
# Scraper delays (polite crawling)
MIN_DELAY=2
MAX_DELAY=5

# Scrape depth
MAX_PAGES=5

# Output
OUTPUT_FORMAT=csv

# Optional: Hunter.io email enrichment
HUNTER_API_KEY=your_key_here

# Optional: Hostinger FTP deployment
HOSTINGER_FTP_HOST=your_host.com
HOSTINGER_FTP_USER=username
HOSTINGER_FTP_PASS=password
```

---

## Testing After Changes

```bash
# 1. Test a single category
python generate_data.py --query "your test query" --location "Hong Kong"

# 2. Test full pipeline
python generate_data.py --force

# 3. Test frontend locally
cd frontend && npm run dev  # http://localhost:4321/hk-jobs/

# 4. Check for errors
python -m pytest tests/ -v
```

---

## Summary: 3 Critical Files

| File | Why | Time |
|------|-----|------|
| **generate_data.py** | Contains Irmin's skill profile, categories, scoring logic | 30 min |
| **Header.astro** | Shows Irmin's name, LinkedIn, GitHub, website | 5 min |
| **Methodology.astro** | Documents Irmin's skill profile | 5 min |

**All other changes are optional.**

