"""
Shared analysis utilities — skill extraction, language detection, salary parsing.
Extracted from export_excel.py so both generate_data.py and export_excel.py
can import without circular dependencies.
"""

import re
import pandas as pd

# ==============================================================================
# SKILLS (HK market)
# ==============================================================================

HARD_SKILLS = {
    "excel", "power bi", "powerbi", "tableau", "looker", "qlik", "sap", "erp", "crm", "salesforce",
    "python", "sql", "r", "java", "javascript", "typescript", "html", "css", "react", "node.js",
    "angular", "vue", "golang", "go", "c++", "c#", ".net", "swift", "kotlin",
    "mysql", "postgresql", "mongodb", "snowflake", "bigquery", "azure", "aws", "gcp",
    "machine learning", "deep learning", "ai", "nlp", "airflow", "dbt", "git", "docker", "kubernetes",
    "terraform", "jenkins", "ci/cd", "api", "rest", "graphql", "microservices",
    "figma", "photoshop", "illustrator", "sketch",
    "seo", "sem", "google ads", "meta ads", "facebook ads",
    "bloomberg", "reuters", "murex", "calypso", "swift messaging",
    "compliance", "aml", "kyc", "risk management", "ifrs", "gaap",
    "hubspot", "jira", "confluence",
    "scrum", "agile", "prince2", "pmp",
    "dashboard", "kpi", "reporting", "bi",
}

SOFT_SKILLS = {"leadership", "teamwork", "communication", "negotiation", "presentation", "analytical"}

MANDARIN_PATTERNS = [
    (r'\bmandarin\s+(?:required|fluent|mandatory|native)\b', 'Required'),
    (r'\bmandarin\s+(?:preferred|advantageous|desirable)\b', 'Preferred'),
    (r'\bputonghua\s+(?:required|fluent|mandatory)\b', 'Required'),
    (r'\bputonghua\s+(?:preferred|advantageous)\b', 'Preferred'),
    (r'\bmandarin\b', 'Yes'),
    (r'\bputonghua\b', 'Yes'),
]


def extract_keywords(desc, hard_only=False):
    if not desc or pd.isna(desc): return []
    text = str(desc).lower()
    pool = HARD_SKILLS if hard_only else HARD_SKILLS | SOFT_SKILLS
    return sorted(kw for kw in pool if re.search(rf'\b{re.escape(kw)}\b', text))


def detect_mandarin(desc):
    if not desc or pd.isna(desc): return ""
    for pattern, label in MANDARIN_PATTERNS:
        if re.search(pattern, str(desc), re.IGNORECASE):
            return label
    return ""


def extract_max_salary(sal):
    """Extract max monthly salary in HKD from salary string."""
    if not sal or pd.isna(sal): return 0
    text = str(sal).replace(",", "").replace("HK$", "").replace("HK", "")
    nums = re.findall(r'\d+', text)
    vals = [int(n) for n in nums if 5000 < int(n) < 500000]
    return max(vals) if vals else 0


def clean_salary(sal, median):
    if not sal or pd.isna(sal):
        return f"~HK${median:,} (estimated)"
    s = str(sal)
    if "negotiable" in s.lower() or "competitive" in s.lower():
        return f"~HK${median:,} (estimated)"
    if extract_max_salary(s) < 5000:
        return f"~HK${median:,} (estimated)"
    return s
