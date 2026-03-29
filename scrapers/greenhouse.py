"""Generic Greenhouse ATS scraper — multiple companies, one API pattern.

Greenhouse is used by many tech/finance companies. The boards API is public:
  GET https://boards-api.greenhouse.io/v1/boards/{company_slug}/jobs?content=true

No auth, no rate limits, full descriptions with content=true.

Companies are configured in GREENHOUSE_COMPANIES below.
Add new ones by finding the slug from their careers page URL:
  e.g., https://boards.greenhouse.io/okx → slug = "okx"
"""

import re
from datetime import datetime
from typing import Optional
from html import unescape

import httpx

from models.job_listing import JobListing
from .base import BaseScraper


# ── Company registry ─────────────────────────────────────────────────────
# slug → display name
GREENHOUSE_COMPANIES = {
    "okx":    "OKX",
    "agoda":  "Agoda",
    "stripe": "Stripe",
    "coinbase": "Coinbase",
    "ripple": "Ripple",
    "bybit":  "Bybit",
}


class GreenhouseScraper(BaseScraper):
    SOURCE = "greenhouse"
    API_BASE = "https://boards-api.greenhouse.io/v1/boards"

    def __init__(self, companies: dict | None = None):
        super().__init__()
        self.companies = companies or GREENHOUSE_COMPANIES

    async def scrape(self, query: str, location: str, max_pages: Optional[int] = None) -> list[JobListing]:
        """Fetch HK jobs from all configured Greenhouse companies."""
        print(f"  [Greenhouse] Scanning {len(self.companies)} companies for Hong Kong jobs...")

        all_listings = []
        async with httpx.AsyncClient(timeout=20, follow_redirects=True) as client:
            for slug, display_name in self.companies.items():
                listings = await self._fetch_company(client, slug, display_name, query)
                all_listings.extend(listings)

        hit_count = len(set(l.company for l in all_listings))
        print(f"  [Greenhouse] Done: {len(all_listings)} jobs from {hit_count} companies")
        return all_listings

    async def _fetch_company(self, client: httpx.AsyncClient, slug: str, display_name: str, query: str) -> list[JobListing]:
        """Fetch all HK postings for one company."""
        url = f"{self.API_BASE}/{slug}/jobs"
        params = {"content": "true"}

        try:
            resp = await client.get(url, params=params)
            if resp.status_code == 404:
                return []
            if resp.status_code != 200:
                return []

            data = resp.json()
            jobs_data = data.get("jobs", [])
            if not jobs_data:
                return []

        except Exception:
            return []

        # Filter to Hong Kong jobs
        hk_jobs = []
        for job in jobs_data:
            loc_name = str(job.get("location", {}).get("name", "")).lower()
            if "hong kong" in loc_name:
                hk_jobs.append(job)

        if not hk_jobs:
            return []

        listings = []
        query_lower = query.lower()
        query_terms = [t for t in query_lower.split() if len(t) > 2]
        for job in hk_jobs:
            listing = self._parse_job(job, display_name)
            if listing:
                title_lower = listing.title.lower()
                desc_lower = listing.description.lower()
                # Match: full phrase in title/desc, OR all terms in title
                if not query_lower \
                   or query_lower in title_lower \
                   or query_lower in desc_lower \
                   or (query_terms and all(t in title_lower for t in query_terms)):
                    listings.append(listing)

        if listings:
            print(f"    {display_name}: {len(listings)} matching jobs (of {len(hk_jobs)} total HK)")

        return listings

    def _parse_job(self, job: dict, company_name: str) -> Optional[JobListing]:
        """Parse a Greenhouse API job into JobListing."""
        title = str(job.get("title", "")).strip()
        if not title:
            return None

        # Location
        location = job.get("location", {}).get("name", "")

        # Description (HTML — strip tags)
        content = job.get("content", "")
        desc = _strip_html(content)[:3000] if content else ""

        # Date
        posting_date = None
        updated = job.get("updated_at") or job.get("created_at")
        if updated:
            try:
                posting_date = datetime.fromisoformat(updated.replace("Z", "+00:00")).date()
            except Exception:
                pass

        # URL
        url = job.get("absolute_url", "")

        # Departments / job type
        departments = job.get("departments", [])
        dept_names = [d.get("name", "") for d in departments if d.get("name")]
        if dept_names and dept_names[0] not in desc:
            desc = f"Department: {', '.join(dept_names)}\n{desc}"

        # Work mode: parse from location string and description
        work_mode = None
        loc_lower = location.lower()
        desc_lower = desc.lower()
        if "remote" in loc_lower:
            work_mode = "Remote"
        elif "hybrid" in loc_lower:
            work_mode = "Hybrid"
        elif re.search(r'\b(fully\s+remote|100%\s+remote|work\s+from\s+home|remote\s+(?:position|role|work))\b', desc_lower):
            work_mode = "Remote"
        elif re.search(r'\b(hybrid|flexible\s+work)\b', desc_lower):
            work_mode = "Hybrid"

        return JobListing(
            title=title,
            company=company_name,
            location=location,
            salary=None,
            description=desc,
            url=url,
            posting_date=posting_date,
            job_type=None,
            work_mode=work_mode,
            source=self.SOURCE,
        )


def _strip_html(html: str) -> str:
    """Strip HTML tags from Greenhouse job content."""
    if not html:
        return ""
    text = re.sub(r'<li>', '- ', html)
    text = re.sub(r'<br\s*/?>', '\n', text)
    text = re.sub(r'<p>', '\n', text)
    text = re.sub(r'<[^>]+>', '', text)
    text = unescape(text)
    # Collapse multiple newlines
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()
