"""JobSpy multi-source scraper — LinkedIn, Indeed, Glassdoor, Google Jobs in one call.

Uses python-jobspy (github.com/speedyapply/JobSpy) to scrape multiple boards.
No API keys, no login, no Selenium. Returns Pandas DataFrame.
"""

import asyncio
from datetime import datetime
from typing import Optional

from models.job_listing import JobListing
from .base import BaseScraper


class JobSpyScraper(BaseScraper):
    SOURCE = "jobspy"  # Individual jobs will have their actual source

    async def scrape(self, query: str, location: str, max_pages: Optional[int] = None) -> list[JobListing]:
        pages = max_pages or self.max_pages
        results_wanted = pages * 25  # ~25 per page

        print(f"  [JobSpy] Scraping LinkedIn + Indeed + Google: '{query}' in {location} ({results_wanted} target)")

        # JobSpy is synchronous — run in thread to not block
        loop = asyncio.get_event_loop()
        listings = await loop.run_in_executor(None, self._scrape_sync, query, location, results_wanted)

        print(f"  [JobSpy] Done: {len(listings)} listings")
        return listings

    def _scrape_sync(self, query: str, location: str, results_wanted: int) -> list[JobListing]:
        from jobspy import scrape_jobs

        try:
            df = scrape_jobs(
                site_name=["linkedin", "indeed", "google"],
                search_term=query,
                location=location if location else "Hong Kong",
                results_wanted=results_wanted,
                hours_old=168,  # last 7 days
                country_indeed="Hong Kong",
            )
        except Exception as e:
            print(f"    JobSpy error: {e}")
            return []

        if df is None or df.empty:
            return []

        listings = []
        for _, row in df.iterrows():
            try:
                listing = self._parse_row(row)
                if listing:
                    listings.append(listing)
            except Exception:
                continue

        sources = df["site"].value_counts().to_dict()
        for src, count in sources.items():
            print(f"    {src}: {count} jobs")

        return listings

    def _parse_row(self, row) -> Optional[JobListing]:
        title = str(row.get("title", "")).strip()
        if not title or title == "nan":
            return None

        company = str(row.get("company", "")).strip()
        if not company or company == "nan":
            company = "Unknown"

        location = str(row.get("location", "")).strip()
        if location == "nan":
            location = ""

        # Salary
        salary = None
        min_amt = row.get("min_amount")
        max_amt = row.get("max_amount")
        currency = row.get("currency", "")
        if min_amt and max_amt and str(min_amt) != "nan" and str(max_amt) != "nan":
            prefix = "HK$" if "HKD" in str(currency) else "$"
            salary = f"{prefix}{int(min_amt):,} - {prefix}{int(max_amt):,}/mo"
        elif max_amt and str(max_amt) != "nan":
            prefix = "HK$" if "HKD" in str(currency) else "$"
            salary = f"{prefix}{int(max_amt):,}/mo"

        description = str(row.get("description", "")).strip()
        if description == "nan":
            description = ""

        posting_date = None
        dp = row.get("date_posted")
        if dp and str(dp) != "nan" and str(dp) != "NaT":
            try:
                if hasattr(dp, "date"):
                    posting_date = dp.date()
                else:
                    posting_date = datetime.fromisoformat(str(dp)).date()
            except Exception:
                pass

        job_type = str(row.get("job_type", "")).strip()
        if job_type == "nan":
            job_type = None

        # Work mode from is_remote + work_from_home_type
        work_mode = None
        is_remote = row.get("is_remote")
        wfh_type = str(row.get("work_from_home_type", "")).strip().lower()
        if wfh_type and wfh_type != "nan":
            if "remote" in wfh_type:
                work_mode = "Remote"
            elif "hybrid" in wfh_type:
                work_mode = "Hybrid"
            elif "onsite" in wfh_type or "on-site" in wfh_type or "office" in wfh_type:
                work_mode = "On-site"
        elif is_remote is True:
            work_mode = "Remote"

        url = str(row.get("job_url", "")).strip()
        if url == "nan":
            url = str(row.get("job_url_direct", "")).strip()
        if url == "nan":
            url = ""

        # Use the actual source site (linkedin, indeed, google, glassdoor)
        source = str(row.get("site", "jobspy")).strip()

        return JobListing(
            title=title,
            company=company,
            location=location,
            salary=salary,
            description=description[:3000],
            url=url,
            posting_date=posting_date,
            job_type=job_type,
            work_mode=work_mode,
            source=source,
        )
