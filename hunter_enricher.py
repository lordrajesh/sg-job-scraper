"""
Hunter.io Enricher — Find recruiter/HR/hiring manager emails for scraped companies.

Reads company names from scraped JSON data, uses Hunter.io domain-search to find
contacts with hiring-relevant titles, verifies emails, stores results.

Usage:
    python hunter_enricher.py                          # enrich all data files
    python hunter_enricher.py --company "Binance"      # single company
    python hunter_enricher.py --check-credits           # check API quota

API key: stored in .env as HUNTER_API_KEY or in GitHub Secrets.
"""

import os
import sys
import json
import re
import time
import argparse
from datetime import datetime

import httpx
from dotenv import load_dotenv

load_dotenv()

HUNTER_API_KEY = os.getenv("HUNTER_API_KEY")
if not HUNTER_API_KEY:
    raise RuntimeError("HUNTER_API_KEY not set in .env or environment")
HUNTER_BASE = "https://api.hunter.io/v2"
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "frontend", "public", "data")
CONTACTS_FILE = os.path.join(DATA_DIR, "contacts.json")
HUNTER_DELAY = 1.2  # seconds between API calls

# Titles we want to find (prioritized for job outreach)
RECRUITER_KEYWORDS = [
    "recruiter", "talent acquisition", "hiring manager", "hr manager",
    "human resources", "people operations", "head of talent",
    "hr director", "hr business partner", "recruitment",
    "staffing", "people & culture", "head of people",
]

DATA_ANALYTICS_KEYWORDS = [
    "data analytics", "analytics manager", "head of data",
    "data science", "bi manager", "head of analytics",
]

PRIORITY_KEYWORDS = RECRUITER_KEYWORDS + DATA_ANALYTICS_KEYWORDS


def check_credits():
    """Check remaining Hunter.io API credits."""
    resp = httpx.get(f"{HUNTER_BASE}/account", params={"api_key": HUNTER_API_KEY})
    if resp.status_code != 200:
        print(f"Error checking credits: {resp.status_code}")
        return None
    data = resp.json().get("data", {})
    calls = data.get("calls", {})
    requests_data = data.get("requests", {})
    print(f"Plan: {data.get('plan_name', 'unknown')} ({data.get('plan_level', 0)})")
    print(f"Searches: {requests_data.get('searches', {}).get('used', 0)} / {requests_data.get('searches', {}).get('available', 0)}")
    print(f"Verifications: {requests_data.get('verifications', {}).get('used', 0)} / {requests_data.get('verifications', {}).get('available', 0)}")
    return data


def domain_search(company: str, domain: str = None):
    """Search for emails at a company domain.
    If no domain provided, Hunter will try to find it from company name."""
    params = {
        "api_key": HUNTER_API_KEY,
        "limit": 20,
        "type": "personal",
    }
    if domain:
        params["domain"] = domain
    else:
        params["company"] = company

    resp = httpx.get(f"{HUNTER_BASE}/domain-search", params=params)
    if resp.status_code != 200:
        return None

    data = resp.json().get("data", {})
    return data


def score_contact(email_entry: dict) -> int:
    """Score a contact for recruiting relevance (0-100)."""
    score = 0
    position = (email_entry.get("position") or "").lower()
    department = (email_entry.get("department") or "").lower()
    seniority = (email_entry.get("seniority") or "").lower()

    # Recruiter/HR = highest priority
    for kw in RECRUITER_KEYWORDS:
        if kw in position or kw in department:
            score += 50
            break

    # Data/analytics leadership = also valuable (hiring managers)
    for kw in DATA_ANALYTICS_KEYWORDS:
        if kw in position or kw in department:
            score += 40
            break

    # Seniority bonus
    if seniority in ("executive", "director"):
        score += 20
    elif seniority == "senior":
        score += 10

    # C-suite
    if re.search(r'\b(ceo|cto|coo|cfo|chro|vp|vice president|director)\b', position):
        score += 15

    # High confidence email
    confidence = email_entry.get("confidence", 0)
    if confidence >= 90:
        score += 10
    elif confidence >= 70:
        score += 5

    return min(100, score)


def verify_email(email: str) -> dict:
    """Verify email deliverability."""
    resp = httpx.get(f"{HUNTER_BASE}/email-verifier",
                     params={"email": email, "api_key": HUNTER_API_KEY})
    if resp.status_code != 200:
        return {"result": "unknown", "score": 0}
    return resp.json().get("data", {})


def enrich_company(company: str) -> dict:
    """Find recruiter/HR contacts for a company."""
    result = {
        "company": company,
        "domain": None,
        "contacts": [],
        "enriched_at": datetime.now().isoformat()[:19],
    }

    # Try domain search by company name
    data = domain_search(company)
    if not data:
        return result

    result["domain"] = data.get("domain", "")
    emails = data.get("emails", [])

    if not emails:
        return result

    # Score and sort contacts by recruiting relevance
    scored = []
    for entry in emails:
        s = score_contact(entry)
        scored.append({
            "email": entry.get("value", ""),
            "first_name": entry.get("first_name", ""),
            "last_name": entry.get("last_name", ""),
            "position": entry.get("position", ""),
            "department": entry.get("department", ""),
            "seniority": entry.get("seniority", ""),
            "linkedin": entry.get("linkedin", ""),
            "phone": entry.get("phone_number", ""),
            "confidence": entry.get("confidence", 0),
            "priority_score": s,
        })

    # Sort by priority score, take top 5
    scored.sort(key=lambda x: x["priority_score"], reverse=True)
    result["contacts"] = scored[:5]

    return result


def load_existing_contacts() -> dict:
    """Load previously enriched contacts."""
    if os.path.exists(CONTACTS_FILE):
        try:
            with open(CONTACTS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def save_contacts(contacts: dict):
    """Save enriched contacts."""
    os.makedirs(os.path.dirname(CONTACTS_FILE), exist_ok=True)
    with open(CONTACTS_FILE, "w", encoding="utf-8") as f:
        json.dump(contacts, f, indent=2, ensure_ascii=False)


def get_unique_companies() -> list[str]:
    """Extract unique company names from all scraped data files."""
    companies = set()
    if not os.path.exists(DATA_DIR):
        return []

    for fname in os.listdir(DATA_DIR):
        if not fname.endswith(".json") or fname in ("index.json", "salary_trends.json", "contacts.json"):
            continue
        try:
            with open(os.path.join(DATA_DIR, fname), "r", encoding="utf-8") as f:
                data = json.load(f)
            for job in data.get("jobs", []):
                company = job.get("company", "")
                if company and company != "Confidential" and company != "Unknown":
                    companies.add(company)
        except Exception:
            pass

    return sorted(companies)


def enrich_all(max_companies: int = 50):
    """Enrich all unique companies from scraped data."""
    credits = check_credits()
    if not credits:
        print("Cannot verify API credits. Aborting.")
        return

    companies = get_unique_companies()
    existing = load_existing_contacts()

    # Skip already enriched (less than 7 days old)
    to_enrich = []
    for company in companies:
        key = company.lower().strip()
        if key in existing:
            enriched = existing[key].get("enriched_at", "")
            if enriched:
                try:
                    age = (datetime.now() - datetime.fromisoformat(enriched)).days
                    if age < 7:
                        continue
                except Exception:
                    pass
        to_enrich.append(company)

    print(f"\nCompanies: {len(companies)} total, {len(to_enrich)} need enrichment")
    to_enrich = to_enrich[:max_companies]
    print(f"Processing: {len(to_enrich)} (capped at {max_companies})")

    enriched_count = 0
    for i, company in enumerate(to_enrich):
        print(f"\n[{i+1}/{len(to_enrich)}] {company}")
        result = enrich_company(company)

        key = company.lower().strip()
        existing[key] = result

        contacts = result.get("contacts", [])
        if contacts:
            top = contacts[0]
            print(f"  Domain: {result['domain']}")
            print(f"  Top contact: {top['first_name']} {top['last_name']} — {top['position']}")
            print(f"  Email: {top['email']} (confidence: {top['confidence']}%, priority: {top['priority_score']})")
            enriched_count += 1
        else:
            print(f"  No contacts found")

        # Save after each company (checkpoint)
        if (i + 1) % 5 == 0 or i == len(to_enrich) - 1:
            save_contacts(existing)
            print(f"  [Checkpoint saved: {len(existing)} companies]")

        time.sleep(HUNTER_DELAY)

    save_contacts(existing)
    print(f"\nDone: {enriched_count}/{len(to_enrich)} companies enriched")
    print(f"Contacts saved to: {CONTACTS_FILE}")


def main():
    parser = argparse.ArgumentParser(description="Hunter.io recruiter email enricher")
    parser.add_argument("--check-credits", action="store_true", help="Check API quota")
    parser.add_argument("--company", help="Enrich a single company")
    parser.add_argument("--max", type=int, default=50, help="Max companies to enrich")
    parser.add_argument("--verify-top", action="store_true", help="Verify top contact emails")
    args = parser.parse_args()

    if args.check_credits:
        check_credits()
        return

    if args.company:
        result = enrich_company(args.company)
        print(json.dumps(result, indent=2))

        if args.verify_top and result["contacts"]:
            top = result["contacts"][0]
            print(f"\nVerifying {top['email']}...")
            v = verify_email(top["email"])
            print(f"  Result: {v.get('result', 'unknown')} (score: {v.get('score', 0)})")
        return

    enrich_all(max_companies=args.max)


if __name__ == "__main__":
    main()
