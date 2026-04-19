"""
Generate JSON data files for the static frontend (Singapore).
Targeted for Employment Pass visa holder profile: fraud analyst, risk analyst, data analyst, business analyst, product/program manager.

Usage:
    python generate_data.py                    # all categories
    python generate_data.py --query "fraud analyst" --location "Singapore"
    python generate_data.py --force            # ignore cache
"""

import asyncio
import json
import os
import sys
import re
import argparse
from collections import Counter
from datetime import datetime

os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from scrapers.jobspy_scraper import JobSpyScraper
from scrapers.jobsdb import JobsDBScraper
from scrapers.lever import LeverScraper
from scrapers.greenhouse import GreenhouseScraper
from merge import deduplicate
from utils.analysis import extract_keywords, detect_mandarin, extract_max_salary, clean_salary, HARD_SKILLS, SOFT_SKILLS

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "frontend", "public", "data")

# ==========================================================================
# CATEGORIES — targeted for Rajesh's profile (Singapore, fraud/risk/analytics)
# Each category has multiple search queries to maximize coverage
# ==========================================================================
CATEGORIES = {
    # Tier 1 — Core fraud/risk/compliance roles
    "fraud-investigator": {
        "label": "Fraud Investigator",
        "queries": ["fraud investigator", "financial crime investigator", "fraud analyst senior"],
    },
    "fraud-analyst": {
        "label": "Fraud Analyst",
        "queries": ["senior fraud analyst", "lead fraud analyst", "fraud analyst senior", "fraud detection analyst"],
    },
    "risk-analyst": {
        "label": "Risk Analyst",
        "queries": ["risk analyst senior", "risk analyst lead", "credit risk analyst"],
    },
    "risk-manager": {
        "label": "Risk Manager",
        "queries": ["risk manager", "senior risk manager", "operational risk manager"],
    },

    # Tier 2 — Data/Business Analysis
    "senior-data-analyst": {
        "label": "Senior Data Analyst",
        "queries": ["senior data analyst", "lead data analyst", "data analyst senior"],
    },
    "business-analyst": {
        "label": "Business Analyst",
        "queries": ["senior business analyst", "business analyst", "business analysis senior"],
    },
    "financial-analyst": {
        "label": "Financial Analyst",
        "queries": ["senior financial analyst", "lead financial analyst", "financial crime analyst senior", "financial data analyst"],
    },

    # Tier 3 — Product/Project/Program Management
    "program-manager": {
        "label": "Program Manager",
        "queries": ["program manager", "senior program manager", "lead program manager"],
    },
    "product-manager": {
        "label": "Product Manager",
        "queries": ["product manager", "senior product manager", "lead product manager"],
    },
    "project-manager": {
        "label": "Project Manager",
        "queries": ["project manager senior", "senior project manager", "lead project manager"],
    },
    "compliance-analyst": {
        "label": "Compliance Analyst",
        "queries": ["senior compliance analyst", "lead compliance analyst", "aml analyst senior", "compliance officer"],
    },
    "data-engineer": {
        "label": "Data Engineer",
        "queries": ["senior data engineer", "lead data engineer", "analytics engineer senior", "big data engineer"],
    },
}

# ==========================================================================
# SKILL MATCH SCORING — against Rajesh's actual stack (SG-focused)
# ==========================================================================
PROFILE_SKILLS = {
    # Weight 3 — expert level (core tools)
    "sql": 3, "power bi": 3, "powerbi": 3, "tableau": 3,
    "python": 3, "microsoft azure": 3, "azure": 3,
    "data analysis": 3, "reporting": 3, "dashboard": 3,
    "visualization": 3, "analytics": 3,

    # Weight 2 — strong (ML/advanced tools)
    "scikit-learn": 2, "xgboost": 2, "sklearn": 2,
    "machine learning": 2, "azure ml": 2, "ml": 2,
    "azure synapse": 2, "synapse": 2, "cosmos db": 2,
    "fraud detection": 2, "risk analysis": 2, "compliance": 2,
    "aml": 2, "kyc": 2, "excel": 2, "ms office": 2,

    # Weight 1 — learning / emerging
    "openai": 1, "prompt engineering": 1, "gpt": 1,
    "api": 1, "rest api": 1, "json": 1,
    "git": 1, "docker": 1, "agile": 1,
    "aws": 1, "gcp": 1, "postgresql": 1,
    "jira": 1, "power automate": 1, "automation": 1,
}


def calc_skill_match(title: str, description: str, skills_found: list) -> int:
    """Score 0-100 based on how well a job matches the profile.
    Also checks job title for role-level relevance."""

    # Title-based relevance (many jobs lack descriptions) — Rajesh's target roles
    TITLE_KEYWORDS = {
        # BANKING TITLES (very common in finance — explicit recognition for accuracy)
        "evp": 33, "executive vice president": 33,
        "svp": 33, "senior vice president": 33,
        "vp": 32, "vice president": 32,
        "avp": 30, "assistant vice president": 30,
        "managing director": 33,
        
        # Top priority — senior/lead fraud/risk/financial crime roles (Rajesh wants SENIOR across ALL categories)
        "senior fraud investigator": 32, "lead fraud investigator": 31,
        "fraud investigator": 30, "financial crime investigator": 30,
        "senior fraud analyst": 30, "lead fraud analyst": 29,
        "fraud analyst": 28, "fraud detection analyst": 27,
        
        # Senior/Lead risk roles
        "senior risk analyst": 27, "lead risk analyst": 26,
        "risk analyst": 25,
        "senior risk manager": 27, "lead risk manager": 26,
        "risk manager": 25, "senior risk": 25,
        
        # Senior/Lead compliance roles
        "senior compliance analyst": 23, "lead compliance analyst": 22,
        "compliance analyst": 20, "aml analyst": 20,
        
        # Data/Business analysts (senior/lead priority)
        "senior data analyst": 26, "lead data analyst": 26,
        "senior business analyst": 26, "lead business analyst": 25,
        "business analyst": 22, "data analyst": 20,
        
        # Senior/Lead financial analysts
        "senior financial analyst": 26, "lead financial analyst": 25,
        "financial analyst": 24, "financial crime analyst": 24,
        
        # Senior/Lead product/program/project management
        "senior program manager": 20, "lead program manager": 19,
        "program manager": 18,
        "senior product manager": 20, "lead product manager": 19,
        "product manager": 18,
        "senior project manager": 20, "lead project manager": 19,
        "project manager": 18,
        
        # Senior/Lead data engineer
        "senior data engineer": 17, "lead data engineer": 16,
        "data engineer": 16, "analytics engineer": 15,
        
        # Supporting technical/domain skills
        "power bi": 20, "tableau": 18, "sql": 15, "python": 14, "analytics": 12,
    }

    title_lower = str(title or "").lower()
    title_score = 0
    for kw, pts in TITLE_KEYWORDS.items():
        if kw in title_lower:
            title_score = max(title_score, pts)

    # Skill-based scoring from description
    text = str(description or "").lower()
    skill_score = 0
    matched_skills = []

    for skill, weight in PROFILE_SKILLS.items():
        if skill in skills_found or re.search(rf'\b{re.escape(skill)}\b', text):
            skill_score += weight
            matched_skills.append(skill)

    # Combine: title relevance + skill matches
    # Title alone can give up to 25, skills can give the rest
    max_skill_score = sum(PROFILE_SKILLS.values())
    skill_pct = (skill_score / max_skill_score) * 75 if max_skill_score > 0 else 0

    # Core skill boost
    core_matches = sum(1 for s in matched_skills if PROFILE_SKILLS.get(s, 0) >= 3)
    if core_matches >= 3:
        skill_pct = min(75, skill_pct * 1.5)
    elif core_matches >= 2:
        skill_pct = min(75, skill_pct * 1.3)

    total = title_score + skill_pct
    return min(100, int(total))


# ==========================================================================
# EMPLOYMENT PASS-FRIENDLY DETECTION (Singapore visa sponsorship)
# ==========================================================================
EP_SIGNALS = [
    r'employment\s+pass', r'work\s+visa', r'visa\s+sponsorship',
    r'work\s+permit', r'work\s+authorisation?', r'work\s+authorization?',
    r'international\s+candidates?', r'overseas\s+candidates?',
    r'diverse\s+team', r'global\s+team', r'multicultural',
    r'international\s+environment', r'expatriate', r'expat',
    r'relocation\s+(?:package|support|assistance)',
    r'open\s+to\s+all\s+nationalit', r'regardless\s+of\s+nationality',
    r'ep\s+eligible', r'\bep\b\s+(?:ready|eligible)',
]

EP_FRIENDLY_COMPANIES = {
    # Global banks (SG presence, known for EP sponsorship)
    "hsbc", "standard chartered", "dbs", "ocbc", "uob",
    "jp morgan", "jpmorgan", "goldman sachs", "morgan stanley",
    "citibank", "citi", "ubs", "barclays", "macquarie", "nomura",
    # Big 4 + consulting
    "deloitte", "pwc", "pricewaterhousecoopers", "ey", "ernst & young",
    "kpmg", "mckinsey", "bcg", "bain", "accenture", "capgemini",
    "oliver wyman", "boston consulting",
    # Tech giants
    "google", "meta", "microsoft", "amazon", "apple", "oracle", "ibm",
    "salesforce", "sap", "adobe", "cisco", "intel",
    # Asian tech
    "alibaba", "tencent", "bytedance", "tiktok", "baidu",
    "grab", "shopee", "lazada", "sea group", "bukalapak",
    # SG fintech / startups
    "revolut", "wise", "stripe", "airwallex", "checkout",
    "razer", "carousell", "ninja van", "edtech",
    # Compliance / Risk / Fraud specialists
    "refinitiv", "moody", "s&p", "reuters", "bloomberg",
    "fenergo", "ascent", "falcon", "featurespace",
    # Fintech / Crypto (if not mandarin-required)
    "binance", "okx", "bybit", "crypto.com", "circle",
}


def detect_ep_friendly(description: str, company: str) -> bool:
    """Check if job/company is likely Employment Pass friendly (Singapore)."""
    text = str(description or "").lower()
    comp = str(company or "").lower()

    # Check company name against known EP-friendly list
    for name in EP_FRIENDLY_COMPANIES:
        if name in comp:
            return True

    # Check description for EP signals
    for pattern in EP_SIGNALS:
        if re.search(pattern, text, re.IGNORECASE):
            return True

    return False


# ==========================================================================
# WORK MODE DETECTION
# ==========================================================================
def detect_work_mode(description: str, job_type: str) -> str:
    """Detect remote/hybrid/on-site from description."""
    text = str(description or "").lower() + " " + str(job_type or "").lower()

    if re.search(r'\b(fully\s+remote|100%\s+remote|work\s+from\s+home|remote\s+(?:position|role|work))\b', text):
        return "Remote"
    if re.search(r'\b(hybrid|flexible\s+work|wfh\s+\d|work\s+from\s+home\s+\d)\b', text):
        return "Hybrid"
    if re.search(r'\b(on[\s-]?site|in[\s-]?office|office[\s-]?based)\b', text):
        return "On-site"
    if re.search(r'\bremote\b', text):
        return "Remote"

    return ""


# ==========================================================================
# SENIORITY DETECTION — Multi-signal approach
# ==========================================================================
def detect_seniority(title: str, description: str, salary: str = "") -> str:
    """
    Detect seniority level using multiple signals:
    - Title keywords (explicit senior/lead/director)
    - Years of experience required (implicit seniority)
    - Responsibility keywords (lead, drive, strategic, mentor)
    - Scope keywords (global, enterprise, cross-functional)
    - Salary level (SGD, implicit seniority)
    
    Returns: "Director+", "Senior", "Manager", "Mid", or "Junior"
    """
    title_lower = str(title or "").lower()
    desc_lower = str(description or "").lower()
    sal_lower = str(salary or "").lower()
    combined = title_lower + " " + desc_lower
    
    seniority_signals = 0
    
    # =================================================================
    # SIGNAL 1: Explicit title keywords (strongest — weight 3)
    # Banking/Financial Institution titles take precedence
    # =================================================================
    # Director+ level: SVP, EVP, Managing Director, Chief, C-suite, VP
    if re.search(r'\b(svp|senior vice president|evp|executive vice president|managing director|md)\b', title_lower):
        return "Director+"  # Senior Vice President / Executive VP = Director+
    
    if re.search(r'\b(vp|vice president|head\s+of|director|chief|c-level)\b', title_lower):
        return "Director+"  # Immediate return for director-level
    
    # Senior level: AVP, Senior, Lead, Principal
    if re.search(r'\b(avp|assistant vice president)\b', title_lower):
        return "Senior"  # AVP (common in banking) = Senior level
    
    if re.search(r'\b(senior|sr\.?|lead|principal)\b', title_lower):
        seniority_signals += 3
    
    # =================================================================
    # SIGNAL 2: Years of experience required (weight 3)
    # =================================================================
    years_match = re.search(r'(\d+)\+?\s*(?:years?|yrs?)\s+(?:of\s+)?(?:experience|exp)', desc_lower)
    if years_match:
        years = int(years_match.group(1))
        if years >= 8:
            seniority_signals += 3  # 8+ years = definitely senior
        elif years >= 6:
            seniority_signals += 2  # 6-7 years = likely senior
        elif years >= 4:
            seniority_signals += 1  # 4-5 years = mid-senior
        # Less than 4 years = no bonus
    
    # =================================================================
    # SIGNAL 3: Responsibility & Leadership keywords (weight 2)
    # =================================================================
    leadership_keywords = [
        r'\b(lead|leading|spearhead|drive|driven|champion)\b',
        r'\b(head\s+of|director|manage|oversight|oversee)\b',
        r'\b(strategic|strategy|strategic\s+partner)\b',
        r'\b(mentor|mentoring|coaching|guide|lead\s+team)\b',
        r'\b(architect|design|develop.*(?:platform|product|solution))\b',
        r'\b(executive\s+(?:stakeholder|leadership)|senior\s+leadership)\b',
    ]
    for kw_pattern in leadership_keywords:
        if re.search(kw_pattern, desc_lower):
            seniority_signals += 2
            break  # Only count once
    
    # =================================================================
    # SIGNAL 4: Scope & Impact keywords (weight 1-2)
    # =================================================================
    scope_keywords = [
        (r'\b(global|worldwide|international|enterprise|cross[\s-]?functional)\b', 2),
        (r'\b(strategic\s+initiative|organizational|company[\s-]?wide|department[\s-]?wide)\b', 1),
    ]
    for pattern, weight in scope_keywords:
        if re.search(pattern, desc_lower):
            seniority_signals += weight
            break  # Only count once
    
    # =================================================================
    # SIGNAL 5: Salary level (weight 2) — SGD/month
    # =================================================================
    # Try to extract salary from salary field or description
    salary_num = 0
    
    # Check salary field first
    if sal_lower:
        sal_match = re.search(r'(?:sgd|s\$|£)?\s*(\d+(?:,\d+)?)', sal_lower)
        if sal_match:
            try:
                salary_num = int(sal_match.group(1).replace(',', ''))
            except:
                pass
    
    # If no explicit salary, try description
    if salary_num == 0:
        sal_patterns = [
            r'(?:sgd|s\$|salary)?\s*(\d+(?:,\d+)?)\s*(?:per\s+month|\/month|monthly)',
            r'(?:sgd|s\$)\s*(\d+(?:,\d+)?)',
        ]
        for pattern in sal_patterns:
            sal_match = re.search(pattern, desc_lower)
            if sal_match:
                try:
                    salary_num = int(sal_match.group(1).replace(',', ''))
                    break
                except:
                    pass
    
    # Map salary to seniority signal
    if salary_num >= 15000:
        seniority_signals += 3  # Senior+ (Rajesh's target minimum is 13K)
    elif salary_num >= 13000:
        seniority_signals += 2  # Senior level
    elif salary_num >= 10000:
        seniority_signals += 1  # Mid-senior
    # Below 10K = no bonus
    
    # =================================================================
    # SIGNAL 6: Negative signals (reduce seniority)
    # =================================================================
    negative_keywords = [
        r'\b(junior|jr\.?|entry[\s-]?level|entry-level|graduate|intern|trainee)\b',
        r'\b(fresh|new\s+to|learn.*and\s+grow|early[\s-]?career)\b',
    ]
    for pattern in negative_keywords:
        if re.search(pattern, title_lower):
            return "Junior"  # Explicit junior indicator
        if re.search(pattern, desc_lower):
            seniority_signals = max(0, seniority_signals - 2)
    
    # =================================================================
    # FINAL DECISION: Map signals to seniority level
    # =================================================================
    if re.search(r'\b(manager|supervisor)\b', title_lower):
        if seniority_signals >= 3:
            return "Senior"
        else:
            return "Manager"
    
    # Based on total signals
    if seniority_signals >= 6:
        return "Senior"
    elif seniority_signals >= 4:
        return "Senior"  # Borderline senior
    elif seniority_signals >= 2:
        return "Mid"
    elif seniority_signals >= 1:
        return "Mid"
    else:
        return "Junior"


# ==========================================================================
# SALARY ESTIMATION — multi-signal model for Singapore market
# ==========================================================================
# Calibrated from verified sources (April 2026):
#   - SG PayScale salary data (payscale.com/research/SG/)
#   - Robert Half Singapore Salary Guide 2026
#   - Glassdoor SG average salaries
# All values in SGD/month.
#
# NOTE: Rajesh's minimum expectation is SGD 13,000/month
# (Currently earning SGD 15,000)

# Base salary by seniority — calibrated from SG market data
# Junior ≈ SGD 3,500-4,500, Mid ≈ SGD 5,500-7,500,
# Senior ≈ SGD 8,500-12,000, Manager ≈ SGD 12,000-18,000,
# Director+ ≈ SGD 18,000-30,000+
SENIORITY_BASE = {
    "Junior":    4000,     # SGD 3,500-4,500
    "Mid":       6500,     # SGD 5,500-7,500 (analyst base)
    "Senior":    10500,    # SGD 8,500-12,000 (senior analyst/specialist)
    "Manager":   15000,    # SGD 12,000-18,000 (manager track)
    "Director+": 25000,    # SGD 18,000-30,000+
}

# Category multiplier — based on SG market role premiums
# Fraud/Risk roles command 15-20% premium in SG due to regulatory demand
# Data roles = baseline
CATEGORY_MULTIPLIER = {
    "Fraud Investigator":     1.20,   # High regulatory demand in SG
    "Fraud Analyst":          1.15,   # Compliance-heavy, premium role
    "Risk Analyst":           1.15,   # Financial risk premium
    "Risk Manager":           1.20,   # Management track + compliance
    "Senior Data Analyst":    1.00,   # Baseline analyst role
    "Business Analyst":       0.95,   # Slightly below senior analyst
    "Financial Analyst":      1.10,   # Finance/fraud combo
    "Program Manager":        1.05,   # Management role
    "Product Manager":        1.08,   # Tech-heavy, slight premium
    "Project Manager":        1.00,   # Baseline PM
    "Compliance Analyst":     1.10,   # Regulatory premium
    "Data Engineer":          1.25,   # Technical infrastructure premium in SG
}

# Company tier — premium/discount based on publicly known SG compensation
COMPANY_TIER = {
    # Tier 1: +30% (major banks, FAANG — documented SG premiums)
    "hsbc": 1.30, "standard chartered": 1.30, "dbs": 1.25,
    "jp morgan": 1.30, "jpmorgan": 1.30, "citi": 1.30,
    "google": 1.35, "meta": 1.35, "microsoft": 1.30,
    "amazon": 1.30, "apple": 1.35,
    # Tier 2: +20% (Big4, major consulting, SG fintech)
    "deloitte": 1.20, "pwc": 1.20, "ey": 1.20, "kpmg": 1.20,
    "mckinsey": 1.25, "bcg": 1.25, "bain": 1.20,
    "stripe": 1.25, "airwallex": 1.20, "wise": 1.15,
    "grab": 1.15, "shopee": 1.15, "sea group": 1.15,
    # Tier 3: +10% (known SG companies)
    "oracle": 1.10, "salesforce": 1.10, "sap": 1.10,
    "binance": 1.15, "crypto.com": 1.10,
    # Baseline (regional/unknown)
}

# Skill premium keywords — capped at +15% total
PREMIUM_SKILLS = {
    "machine learning": 0.05, "deep learning": 0.05, "pytorch": 0.05,
    "tensorflow": 0.05, "kubernetes": 0.03, "aws": 0.03, "azure": 0.03,
    "blockchain": 0.05, "smart contract": 0.05, "solidity": 0.05,
    "quantitative": 0.05, "algorithmic trading": 0.08,
}


def estimate_salary(seniority: str, company: str, category_label: str,
                    description: str, ep_friendly: bool) -> dict:
    """Estimate monthly SGD salary when not disclosed.
    Returns {"estimate": int, "confidence": str, "basis": str}."""

    # Step 1: Seniority base
    base = SENIORITY_BASE.get(seniority, SENIORITY_BASE["Mid"])

    # Step 2: Category multiplier
    cat_mult = CATEGORY_MULTIPLIER.get(category_label, 1.0)

    # Step 3: Company tier
    comp_lower = str(company or "").lower()
    comp_mult = 1.0
    for name, mult in COMPANY_TIER.items():
        if name in comp_lower:
            comp_mult = mult
            break

    # Step 4: EP premium (Employment Pass companies tend to pay more)
    ep_mult = 1.05 if ep_friendly and comp_mult == 1.0 else 1.0

    # Step 5: Skill premiums from description
    desc_lower = str(description or "").lower()
    skill_bonus = 0.0
    for skill, bonus in PREMIUM_SKILLS.items():
        if skill in desc_lower:
            skill_bonus += bonus
    skill_mult = 1.0 + min(skill_bonus, 0.15)  # Cap at +15%

    # Combine
    estimate = int(base * cat_mult * comp_mult * ep_mult * skill_mult)

    # Round to nearest 500
    estimate = round(estimate / 500) * 500

    # Confidence based on how many signals contributed
    signals = sum([
        seniority != "Mid",       # Seniority detected (not default)
        comp_mult != 1.0,         # Known company tier
        cat_mult != 1.0,          # Category has a multiplier
        skill_bonus > 0,          # Premium skills found
    ])
    if signals >= 3:
        confidence = "High"
    elif signals >= 1:
        confidence = "Medium"
    else:
        confidence = "Low"

    # Basis explanation
    parts = [seniority + "-level"]
    if comp_mult != 1.0:
        parts.append(company.split()[0] + " tier")
    if cat_mult != 1.0:
        parts.append(category_label.split()[0] + " role")
    basis = ", ".join(parts)

    return {"estimate": estimate, "confidence": confidence, "basis": basis}


# ==========================================================================
# SCRAPING
# ==========================================================================
async def _safe_scrape(scraper, query, location, pages, name):
    """Run a scraper with error isolation."""
    try:
        return await scraper.scrape(query, location, pages)
    except Exception as e:
        print(f"    {name}: {str(e)[:80]}")
        return []


async def scrape_all(query: str, location: str, pages: int = 2):
    """Run all sources in parallel (JobSpy + JobsDB + Lever + Greenhouse)."""
    jobspy = JobSpyScraper()
    jobsdb = JobsDBScraper()
    lever = LeverScraper()
    greenhouse = GreenhouseScraper()

    results = await asyncio.gather(
        _safe_scrape(jobspy, query, location, pages, "jobspy"),
        _safe_scrape(jobsdb, query, location, pages, "jobsdb"),
        _safe_scrape(lever, query, location, pages, "lever"),
        _safe_scrape(greenhouse, query, location, pages, "greenhouse"),
        return_exceptions=True,
    )

    all_listings = []
    for r in results:
        if isinstance(r, list):
            all_listings.extend(r)
    return all_listings


async def scrape_category(category_slug: str, location: str, pages: int = 2):
    """Scrape all queries for a category and merge results."""
    cat = CATEGORIES[category_slug]
    all_listings = []

    for query in cat["queries"]:
        listings = await scrape_all(query, location, pages)
        all_listings.extend(listings)

    return deduplicate(all_listings)


# ==========================================================================
# CATEGORY RELEVANCE — how well a job title matches the selected category
# ==========================================================================
# Maps category label → title keywords that indicate strong relevance
CATEGORY_TITLE_KEYWORDS = {
    "Fraud Investigator":     ["avp fraud investigator", "vp fraud", "senior fraud investigator", "lead fraud investigator", "fraud investigator", "financial crime investigator"],
    "Fraud Analyst":          ["avp fraud analyst", "vp fraud analyst", "senior fraud analyst", "lead fraud analyst", "fraud analyst", "fraud detection analyst"],
    "Risk Analyst":           ["avp risk", "vp risk analyst", "senior risk analyst", "lead risk analyst", "risk analyst", "credit risk analyst"],
    "Risk Manager":           ["avp risk manager", "vp risk", "senior risk manager", "lead risk manager", "risk manager", "head of risk"],
    "Senior Data Analyst":    ["avp data", "vp analytics", "senior data analyst", "lead data analyst", "data analyst lead"],
    "Business Analyst":       ["avp business", "vp business analyst", "senior business analyst", "lead business analyst", "business analyst", "business analysis"],
    "Financial Analyst":      ["avp financial", "vp financial analyst", "senior financial analyst", "lead financial analyst", "financial analyst", "financial crime analyst"],
    "Program Manager":        ["avp program", "vp program", "senior program manager", "lead program manager", "program manager", "programme manager"],
    "Product Manager":        ["avp product", "vp product", "senior product manager", "lead product manager", "product manager"],
    "Project Manager":        ["avp project", "vp project", "senior project manager", "lead project manager", "project manager", "project lead"],
    "Compliance Analyst":     ["avp compliance", "vp compliance", "senior compliance analyst", "lead compliance analyst", "compliance analyst", "aml analyst"],
    "Data Engineer":          ["avp engineering", "vp engineering", "senior data engineer", "lead data engineer", "data engineer", "analytics engineer"],
}


def calc_category_relevance(title: str, description: str, category_label: str, salary: str = "") -> int:
    """Score 0-100: how relevant is this job to the selected category.
    Rajesh targets SENIOR-level roles across all categories.
    Uses enhanced multi-signal seniority detection (title, experience, responsibility, scope, salary)."""
    keywords = CATEGORY_TITLE_KEYWORDS.get(category_label, [])
    if not keywords:
        return 0

    title_lower = str(title or "").lower()
    desc_lower = str(description or "").lower()

    # Title match is strongest signal (0-60 pts)
    title_score = 0
    for kw in keywords:
        if kw in title_lower:
            title_score = 60
            break

    # Description match is weaker (0-40 pts)
    desc_hits = sum(1 for kw in keywords if kw in desc_lower)
    desc_score = min(40, desc_hits * 15)

    base_score = min(100, title_score + desc_score)

    # SENIORITY BOOST — Rajesh targets Senior/Lead roles across all categories
    # Use enhanced seniority detection that considers:
    # - Title keywords (senior, lead, principal, director)
    # - Years of experience (6+, 8+)
    # - Responsibility keywords (lead, drive, strategic, mentor)
    # - Scope keywords (global, enterprise, cross-functional)
    # - Salary level (13K+ SGD = senior)
    detected_seniority = detect_seniority(title, description, salary)
    
    seniority_bonus = 0
    if detected_seniority == "Director+":
        seniority_bonus = 18  # Highest priority
    elif detected_seniority == "Senior":
        seniority_bonus = 15  # Target level
    elif detected_seniority == "Manager":
        seniority_bonus = 12  # Good (manager-level responsibility)
    elif detected_seniority == "Mid":
        seniority_bonus = 5   # Borderline
    else:  # Junior
        seniority_bonus = -10  # Penalize junior roles

    return min(100, max(0, base_score + seniority_bonus))


# ==========================================================================
# BUILD JSON
# ==========================================================================
def build_json(listings, query_label, location):
    """Convert listings to JSON with skill match + EP sponsorship scoring."""
    jobs = []
    all_hard = []
    all_soft = []

    sal_values = []
    for l in listings:
        ms = extract_max_salary(l.salary)
        if ms > 0:
            sal_values.append(ms)

    median_sal = int(sorted(sal_values)[len(sal_values) // 2]) if sal_values else 0

    for l in listings:
        # Skip Mandarin detection — not relevant for Rajesh (non-Mandarin speaker)
        # mandarin = detect_mandarin(l.description)
        mandarin = ""
        
        skills = extract_keywords(l.description, True)
        soft = [kw for kw in SOFT_SKILLS if re.search(rf'\b{re.escape(kw)}\b', str(l.description or "").lower())]
        ms = extract_max_salary(l.salary)
        match_score = calc_skill_match(l.title, l.description, skills)
        relevance = calc_category_relevance(l.title, l.description, query_label, l.salary)
        ep_friendly = detect_ep_friendly(l.description, l.company)
        # Use work_mode from scraper if available, otherwise detect from description
        work_mode = l.work_mode if l.work_mode else detect_work_mode(l.description, l.job_type)
        # Detect seniority with salary signal
        seniority = detect_seniority(l.title, l.description, l.salary)

        all_hard.extend(skills)
        all_soft.extend(soft)

        company = l.company if l.company and l.company != "Unknown" else "Confidential"

        # Salary: real if available, otherwise estimate
        sal_display = l.salary or ""
        sal_est = None
        sal_confidence = ""
        sal_basis = ""
        if not sal_display or "negotiable" in sal_display.lower() or "competitive" in sal_display.lower():
            est = estimate_salary(seniority, company, query_label, l.description, ep_friendly)
            sal_display = f"~SGD {est['estimate']:,}"
            sal_est = est["estimate"]
            sal_confidence = est["confidence"]
            sal_basis = est["basis"]

        jobs.append({
            "title": l.title,
            "company": company,
            "location": l.location or location,
            "salary": sal_display,
            "salary_num": ms if ms > 0 else (sal_est or 0),
            "salary_est": sal_est,
            "salary_confidence": sal_confidence,
            "salary_basis": sal_basis,
            "mandarin": mandarin or "",
            "skills": skills if skills else [],
            "type": l.job_type or "",
            "date": str(l.posting_date or "")[:10],
            "source": l.source,
            "url": l.url or "",
            "match": match_score,
            "relevance": relevance,
            "ep_friendly": ep_friendly,
            "work_mode": work_mode,
            "seniority": seniority,
        })

    # Salary brackets (SGD monthly) — includes estimates for chart usefulness
    # Rajesh's minimum: SGD 13,000
    brackets = {
        "<SGD 8K": 0, "SGD 8-12K": 0, "SGD 12-16K": 0,
        "SGD 16-20K": 0, "SGD 20-30K": 0, "SGD 30K+": 0,
    }
    all_sal_for_brackets = [j["salary_num"] for j in jobs if j["salary_num"] > 0]
    for s in all_sal_for_brackets:
        if s < 8000: brackets["<SGD 8K"] += 1
        elif s < 12001: brackets["SGD 8-12K"] += 1
        elif s < 16001: brackets["SGD 12-16K"] += 1
        elif s < 20001: brackets["SGD 16-20K"] += 1
        elif s < 30001: brackets["SGD 20-30K"] += 1
        else: brackets["SGD 30K+"] += 1

    # Median now uses real + estimated
    all_sal_nums = sorted([j["salary_num"] for j in jobs if j["salary_num"] > 0])
    median_sal = all_sal_nums[len(all_sal_nums) // 2] if all_sal_nums else 0
    est_count = sum(1 for j in jobs if j.get("salary_est"))

    hard_counts = Counter(all_hard).most_common(15)
    soft_counts = Counter(all_soft).most_common(5)

    top3_skills = [s for s, _ in hard_counts[:3]]
    for j in jobs:
        if not j["skills"] and top3_skills:
            j["skills"] = top3_skills

    company_counts = Counter(j["company"] for j in jobs if j["company"] != "Confidential")

    # Sort by category relevance first, then match score as tiebreaker
    jobs.sort(key=lambda j: (j["relevance"], j["match"]), reverse=True)

    return {
        "meta": {
            "query": query_label,
            "location": location,
            "generated": datetime.now().isoformat()[:19],
            "total": len(jobs),
            "sources": list(set(j["source"] for j in jobs)),
        },
        "stats": {
            "total_jobs": len(jobs),
            "total_companies": len(set(j["company"] for j in jobs)),
            "salary_median": median_sal,
            "salary_minimum_target": 13000,  # Rajesh's minimum expectation
            "with_salary": len(sal_values),
            "with_estimate": est_count,
            "ep_friendly": sum(1 for j in jobs if j["ep_friendly"]),
            "avg_match": int(sum(j["match"] for j in jobs) / len(jobs)) if jobs else 0,
        },
        "charts": {
            "salary_brackets": brackets,
            "top_skills": [{"skill": k, "count": c} for k, c in hard_counts],
            "soft_skills": [{"skill": k, "count": c} for k, c in soft_counts],
            "top_companies": [{"name": k, "count": c} for k, c in company_counts.most_common(10)],
        },
        "jobs": jobs,
    }


# ==========================================================================
# CACHING + FILE GENERATION
# ==========================================================================
CACHE_MAX_AGE_HOURS = 20


def is_cache_fresh(filepath: str) -> bool:
    if not os.path.exists(filepath):
        return False
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        generated = data.get("meta", {}).get("generated", "")
        if not generated:
            return False
        gen_time = datetime.fromisoformat(generated)
        age_hours = (datetime.now() - gen_time).total_seconds() / 3600
        return age_hours < CACHE_MAX_AGE_HOURS
    except Exception:
        return False


async def generate_single(query: str, location: str, query_label: str,
                          pages: int = 2, force: bool = False, category_slug: str = None):
    """Generate data for a single category+location combo."""
    slug = f"{(category_slug or query).replace(' ', '-')}_{location.replace(' ', '-').lower()}"
    filepath = os.path.join(DATA_DIR, f"{slug}.json")

    if not force and is_cache_fresh(filepath):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            age = datetime.now() - datetime.fromisoformat(data["meta"]["generated"])
            hours = int(age.total_seconds() / 3600)
            print(f"  CACHED: {query_label} in {location} ({data['stats']['total_jobs']} jobs, {hours}h old)")
            return filepath
        except Exception:
            pass

    print(f"  Scraping: {query_label} in {location}...")

    # Use multi-query category scrape if we have a category slug
    if category_slug and category_slug in CATEGORIES:
        listings = await scrape_category(category_slug, location, pages)
    else:
        raw_listings = await scrape_all(query, location, pages)
        listings = deduplicate(raw_listings) if raw_listings else []

    if not listings:
        print(f"    No results")
        return None

    data = build_json(listings, query_label, location)

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=True, indent=2)

    print(f"    {data['stats']['total_jobs']} jobs (avg match: {data['stats']['avg_match']}%, "
          f"TTPS-friendly: {data['stats']['ttps_friendly']}) -> {os.path.basename(filepath)}")

    return filepath


def _update_index(categories_labels, data_entries, scraped_counts):
    """Write the master index.json."""
    index_path = os.path.join(DATA_DIR, "index.json")
    with open(index_path, "w", encoding="utf-8") as f:
        json.dump({
            "categories": categories_labels,
            "data": data_entries,
            "scraped_counts": scraped_counts,
            "generated": datetime.now().isoformat()[:19],
        }, f, ensure_ascii=False, indent=2)


async def fetch_salary_trends():
    """Salary trends placeholder."""
    trends_path = os.path.join(DATA_DIR, "salary_trends.json")
    if os.path.exists(trends_path):
        try:
            with open(trends_path, "r", encoding="utf-8") as f:
                return json.load(f).get("trends", {})
        except Exception:
            pass

    with open(trends_path, "w", encoding="utf-8") as f:
        json.dump({"trends": {}, "generated": datetime.now().isoformat()[:19]},
                  f, ensure_ascii=True, indent=2)
    print("  Salary trends: will build from scraped data over time")
    return {}


# ==========================================================================
# MAIN GENERATION
# ==========================================================================
CONCURRENCY = 3
LOCATION = "Hong Kong"  # Single location — HK is small, no district split


async def generate_all(pages: int = 5, force: bool = False, **_kwargs):
    print("=" * 60)
    print("HK JOB SCRAPER — TARGETED PROFILE SEARCH")
    print(f"Categories: {len(CATEGORIES)}")
    print(f"Queries per category: {sum(len(c['queries']) for c in CATEGORIES.values())} total search terms")
    print(f"Location: {LOCATION}")
    print(f"Cache: {'DISABLED (--force)' if force else f'skip if < {CACHE_MAX_AGE_HOURS}h old'}")
    print(f"Concurrency: {CONCURRENCY} categories at once")
    print("=" * 60)

    os.makedirs(DATA_DIR, exist_ok=True)
    await fetch_salary_trends()

    sem = asyncio.Semaphore(CONCURRENCY)
    index_entries = []

    async def process_category(cat_slug, cat_info):
        async with sem:
            path = await generate_single(
                query=cat_slug.replace("-", " "),
                location=LOCATION,
                query_label=cat_info["label"],
                pages=pages,
                force=force,
                category_slug=cat_slug,
            )
            if path:
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        fdata = json.load(f)
                    return {
                        "query": cat_info["label"],
                        "location": LOCATION,
                        "file": os.path.basename(path),
                        "slug": f"{cat_slug}_{LOCATION.replace(' ', '-').lower()}",
                        "total_jobs": fdata.get("stats", {}).get("total_jobs", 0),
                    }
                except Exception:
                    pass
            return None

    results = await asyncio.gather(*[
        process_category(slug, info) for slug, info in CATEGORIES.items()
    ], return_exceptions=True)

    for r in results:
        if isinstance(r, dict):
            index_entries.append(r)

    scraped_counts = {}
    for entry in index_entries:
        scraped_counts[entry["query"]] = entry["total_jobs"]

    categories_labels = [c["label"] for c in CATEGORIES.values()]
    _update_index(categories_labels, index_entries, scraped_counts)

    total_jobs = sum(e["total_jobs"] for e in index_entries)
    print(f"\nDone: {len(index_entries)} categories, {total_jobs} total jobs")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--query", help="Single query (e.g. 'data analyst')")
    parser.add_argument("--location", default="Hong Kong")
    parser.add_argument("--pages", type=int, default=5)
    parser.add_argument("--force", action="store_true", help="Ignore cache, re-scrape everything")
    args = parser.parse_args()

    if args.query:
        asyncio.run(generate_single(args.query, args.location, args.query.title(),
                                    args.pages, force=args.force))
    else:
        asyncio.run(generate_all(args.pages, force=args.force))


if __name__ == "__main__":
    main()
