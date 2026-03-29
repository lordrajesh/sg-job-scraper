"""JobsDB Hong Kong scraper — GraphQL API (reverse-engineered).

JobsDB (owned by SEEK) exposes a GraphQL endpoint at hk.jobsdb.com/graphql.
- Cloudflare blocks HTML pages but NOT the GraphQL API
- No search query exposed — we scan job IDs by range
- HK zone = "asia-1"
- Job IDs are sequential 8-digit integers shared across all SEEK sites
- We fetch jobDetails(id) for enrichment: title, company, salary, location, description

Strategy: Scan recent job IDs, filter by sourceZone="asia-1" (HK).
"""

import re
import asyncio
from datetime import datetime, date
from typing import Optional
from html import unescape

import httpx

from models.job_listing import JobListing
from .base import BaseScraper
from utils.helpers import get_user_agent


JOBDETAILS_QUERY = """
query JobDetails($id: ID!) {
    jobDetails(id: $id) {
        job {
            id
            title
            abstract
            content
            sourceZone
            advertiser { id name }
            salary { label }
            location { label }
            listedAt { dateTimeUtc shortAbsoluteLabel }
            workTypes { label }
        }
    }
}
"""


class JobsDBScraper(BaseScraper):
    SOURCE = "jobsdb"
    GRAPHQL_URL = "https://hk.jobsdb.com/graphql"
    HK_ZONE = "asia-1"

    async def scrape(self, query: str, location: str, max_pages: Optional[int] = None) -> list[JobListing]:
        """Grab ALL recent HK jobs from JobsDB via GraphQL ID scanning.

        ~15% of SEEK IDs are HK (asia-1). We scan backwards from the latest ID
        in parallel batches of 10, collecting every HK job we find.
        Keyword filtering happens later on the frontend/generate_data layer.

        pages controls volume: each "page" = ~50 HK jobs collected.
        """
        pages = max_pages or self.max_pages
        target = pages * 50
        listings: list[JobListing] = []

        print(f"  [JobsDB] Collecting latest {target} HK jobs via GraphQL...")

        headers = {
            "User-Agent": get_user_agent(),
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Origin": "https://hk.jobsdb.com",
            "Referer": "https://hk.jobsdb.com/",
        }

        async with httpx.AsyncClient(headers=headers, verify=False, timeout=15) as client:
            latest_id = await self._find_latest_id(client)
            if not latest_id:
                print("    Could not determine latest job ID range")
                return []

            print(f"    Starting from ID ~{latest_id:,}")

            concurrent = 10
            scanned = 0
            max_scan = target * 8  # ~15% are HK → scan ~8x target

            current_id = latest_id
            while len(listings) < target and scanned < max_scan:
                batch_ids = list(range(current_id, current_id - concurrent, -1))
                current_id -= concurrent
                scanned += concurrent

                tasks = [self._fetch_job(client, str(jid)) for jid in batch_ids]
                results = await asyncio.gather(*tasks, return_exceptions=True)

                for job_data in results:
                    if isinstance(job_data, Exception) or not job_data:
                        continue
                    job = job_data.get("job")
                    if not job or job.get("sourceZone") != self.HK_ZONE:
                        continue

                    listing = self._parse_graphql(job)
                    if listing:
                        listings.append(listing)

                await asyncio.sleep(0.1)

            print(f"    Scanned {scanned} IDs → {len(listings)} HK jobs")

        print(f"  [JobsDB] Done: {len(listings)} listings (with descriptions)")
        return listings

    async def _find_latest_id(self, client: httpx.AsyncClient) -> Optional[int]:
        """Binary search for the latest active job ID."""
        # Start high, work down
        for probe in [90000000, 88000000, 86000000, 85000000, 84000000, 83000000, 82000000]:
            job = await self._fetch_job(client, str(probe))
            if job and job.get("job"):
                return probe
        return 85000000  # fallback

    async def _fetch_job(self, client: httpx.AsyncClient, job_id: str) -> Optional[dict]:
        """Fetch a single job via GraphQL."""
        try:
            resp = await client.post(self.GRAPHQL_URL, json={
                "query": JOBDETAILS_QUERY,
                "variables": {"id": job_id},
            })
            if resp.status_code != 200:
                return None
            data = resp.json()
            return data.get("data", {}).get("jobDetails")
        except Exception:
            return None

    def _matches_query(self, query: str, title: str, abstract: str, content: str) -> bool:
        """Check if the job matches the search query."""
        terms = query.split()
        text = f"{title} {abstract} {content}"
        return all(term in text for term in terms)

    def _parse_graphql(self, job: dict) -> Optional[JobListing]:
        """Parse GraphQL job response into JobListing."""
        title = job.get("title", "")
        if not title:
            return None
        title = re.sub(r'<[^>]+>', '', title).strip()

        advertiser = job.get("advertiser") or {}
        company = advertiser.get("name") or "Unknown"

        location = ""
        loc = job.get("location")
        if loc:
            location = loc.get("label", "")

        salary_obj = job.get("salary")
        salary = salary_obj.get("label") if salary_obj else None

        # Description: use content (full HTML) or abstract (summary)
        content = job.get("content", "")
        abstract = job.get("abstract", "")
        description = self._strip_html(content) if content else abstract

        posting_date = None
        listed = job.get("listedAt")
        if listed:
            try:
                dt_str = listed.get("dateTimeUtc", "")
                if dt_str:
                    posting_date = datetime.fromisoformat(dt_str.replace("Z", "+00:00")).date()
            except Exception:
                pass

        work_types = job.get("workTypes")
        job_type = work_types.get("label") if work_types else None

        job_id = job.get("id", "")
        url = f"https://hk.jobsdb.com/job/{job_id}" if job_id else ""

        return JobListing(
            title=title,
            company=company,
            location=location,
            salary=salary,
            description=description,
            url=url,
            posting_date=posting_date,
            job_type=job_type,
            source=self.SOURCE,
        )

    @staticmethod
    async def fetch_job_by_id(job_id: str) -> Optional[dict]:
        """Public method to fetch a single job by ID (for enrichment)."""
        headers = {
            "Content-Type": "application/json",
            "Origin": "https://hk.jobsdb.com",
        }
        async with httpx.AsyncClient(headers=headers, verify=False, timeout=10) as client:
            resp = await client.post("https://hk.jobsdb.com/graphql", json={
                "query": JOBDETAILS_QUERY,
                "variables": {"id": job_id},
            })
            if resp.status_code == 200:
                data = resp.json()
                return data.get("data", {}).get("jobDetails", {}).get("job")
        return None

    @staticmethod
    def _strip_html(html: str) -> str:
        if not html:
            return ""
        text = re.sub(r'<br\s*/?>', '\n', html)
        text = re.sub(r'<[^>]+>', '', text)
        text = unescape(text)
        text = re.sub(r'\n{3,}', '\n\n', text)
        return text.strip()[:3000]
