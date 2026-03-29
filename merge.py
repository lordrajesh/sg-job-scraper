"""
Cross-platform job deduplication and merging
=============================================
Handles 4 sources (LinkedIn, Indeed, Google, JobsDB) with 3 dedup layers:
1. URL dedup — exact match on canonical URL
2. Title+Company dedup — same title + same company = same job
3. Fuzzy dedup — similar title (0.7+) + similar company (0.5+) across sources
"""

import re
from difflib import SequenceMatcher
from urllib.parse import urlparse
from models.job_listing import JobListing


def normalize(text: str) -> str:
    if not text:
        return ""
    t = text.lower().strip()
    t = re.sub(r'[^a-z0-9\s]', '', t)
    t = re.sub(r'\s+', ' ', t)
    return t


def canonical_url(url: str) -> str:
    """Strip tracking params to get a comparable URL."""
    if not url:
        return ""
    parsed = urlparse(url)
    # Keep scheme + host + path, drop query/fragment
    return f"{parsed.scheme}://{parsed.netloc}{parsed.path}".rstrip("/").lower()


def similarity(a: str, b: str) -> float:
    a, b = normalize(a), normalize(b)
    if not a or not b:
        return 0.0
    if a == b:
        return 1.0
    return SequenceMatcher(None, a, b).ratio()


GENERIC_COMPANIES = {"confidential", "unknown", "empresa confidencial", "confidencial", ""}


def _is_generic_company(company: str) -> bool:
    return normalize(company) in GENERIC_COMPANIES


def is_same_job(a: JobListing, b: JobListing) -> bool:
    """Check if two listings are the same job, even across platforms."""
    # Layer 1: URL match — always definitive
    url_a = canonical_url(a.url)
    url_b = canonical_url(b.url)
    if url_a and url_b and url_a == url_b:
        return True

    # Skip title/company matching for generic companies — many different jobs share the same title
    if _is_generic_company(a.company) or _is_generic_company(b.company):
        return False

    # Layer 2: Exact title + company
    na = normalize(a.title)
    nb = normalize(b.title)
    ca = normalize(a.company)
    cb = normalize(b.company)
    if na and nb and ca and cb:
        if na == nb and ca == cb:
            return True

    # Layer 3: Fuzzy match (title 0.7+ AND company 0.5+)
    title_sim = similarity(a.title, b.title)
    company_sim = similarity(a.company, b.company)
    if title_sim >= 0.7 and company_sim >= 0.5:
        return True

    # Very strong title match + same location
    if title_sim >= 0.9 and normalize(a.location) == normalize(b.location):
        return True

    return False


def pick_best(field_a, field_b):
    a = str(field_a).strip() if field_a else ""
    b = str(field_b).strip() if field_b else ""
    if not a:
        return b
    if not b:
        return a
    return a if len(a) >= len(b) else b


def _pick_best_listing(a: JobListing, b: JobListing) -> JobListing:
    """Pick the listing with the most data, enriching from the other."""
    # Prefer the one with a description
    if a.description and not b.description:
        winner, donor = a, b
    elif b.description and not a.description:
        winner, donor = b, a
    # Prefer the one with salary
    elif a.salary and not b.salary:
        winner, donor = a, b
    elif b.salary and not a.salary:
        winner, donor = b, a
    # Prefer jobsdb (has full descriptions)
    elif a.source == "jobsdb":
        winner, donor = a, b
    elif b.source == "jobsdb":
        winner, donor = b, a
    else:
        winner, donor = a, b

    # Enrich winner with donor's data where winner is missing
    if not winner.salary and donor.salary:
        winner.salary = donor.salary
    if not winner.description and donor.description:
        winner.description = donor.description
    if not winner.job_type and donor.job_type:
        winner.job_type = donor.job_type
    if not winner.posting_date and donor.posting_date:
        winner.posting_date = donor.posting_date

    return winner


def deduplicate(listings: list[JobListing]) -> list[JobListing]:
    """Remove duplicates across all sources. Returns unique listings only,
    enriched with the best data from each duplicate."""
    if not listings:
        return []

    unique: list[JobListing] = []
    seen_urls: set[str] = set()
    seen_title_company: set[str] = set()

    for listing in listings:
        # Fast check: URL dedup
        curl = canonical_url(listing.url)
        if curl and curl in seen_urls:
            continue

        # Fast check: exact title+company (skip for generic companies)
        key = f"{normalize(listing.title)}||{normalize(listing.company)}"
        is_generic = _is_generic_company(listing.company)

        if not is_generic and key in seen_title_company:
            # Find the existing one and enrich it
            for i, existing in enumerate(unique):
                ekey = f"{normalize(existing.title)}||{normalize(existing.company)}"
                if ekey == key:
                    unique[i] = _pick_best_listing(existing, listing)
                    break
            if curl:
                seen_urls.add(curl)
            continue

        # Slow check: fuzzy match against existing
        matched = False
        for i, existing in enumerate(unique):
            if is_same_job(existing, listing):
                unique[i] = _pick_best_listing(existing, listing)
                matched = True
                break

        if not matched:
            unique.append(listing)
            if curl:
                seen_urls.add(curl)
            if not is_generic:
                seen_title_company.add(key)

    return unique


def deduplicate_and_merge(listings: list[JobListing]) -> tuple[list[dict], list[JobListing]]:
    """Legacy interface — returns (merged_pairs, unique_singles).
    Now just deduplicates and returns all as singles."""
    unique = deduplicate(listings)
    removed = len(listings) - len(unique)
    return [], unique  # No merged pairs, just clean unique list
