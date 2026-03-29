"""Base scraper class — all site-specific scrapers inherit from this."""

import abc
import asyncio
from typing import Optional

from models.job_listing import JobListing
from config import MAX_PAGES
from utils.helpers import get_user_agent, async_delay, save_results


class BaseScraper(abc.ABC):
    """Abstract base for job board scrapers."""

    SOURCE: str = ""  # Override in subclass

    def __init__(self):
        self.max_pages = MAX_PAGES
        self.headers = {
            "User-Agent": get_user_agent(),
            "Accept-Language": "en-HK,en;q=0.9,zh-HK;q=0.8,zh;q=0.7",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        }

    @abc.abstractmethod
    async def scrape(self, query: str, location: str, max_pages: Optional[int] = None) -> list[JobListing]:
        """Scrape job listings. Must be implemented by each site scraper."""
        ...

    async def polite_delay(self):
        await async_delay()

    def save(self, listings: list[JobListing], query: str, location: str) -> Optional[str]:
        return save_results(listings, query, location, self.SOURCE)

    def run(self, query: str, location: str, max_pages: Optional[int] = None) -> list[JobListing]:
        """Synchronous wrapper for scrape()."""
        return asyncio.run(self.scrape(query, location, max_pages))
