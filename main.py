"""
Hong Kong Job Scraper — Free, fast, API-first
===============================================
Uses Adzuna HK (aggregator) + JobsDB APIs.
No Selenium. No blocking risk.

Usage:
    python main.py                                          # default: "data analyst" in Hong Kong
    python main.py --query "python developer" --location "Central"
    python main.py --sites adzuna                           # adzuna only
    python main.py --sites adzuna jobsdb                    # both
"""

import argparse
import asyncio
import time
import sys
import os

os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from scrapers.jobspy_scraper import JobSpyScraper
from scrapers.jobsdb import JobsDBScraper
from scrapers.lever import LeverScraper
from scrapers.greenhouse import GreenhouseScraper
from export_excel import generate_excel
from merge import deduplicate
from utils.helpers import save_results


SCRAPERS = {
    "jobspy": JobSpyScraper,
    "jobsdb": JobsDBScraper,
    "lever": LeverScraper,
    "greenhouse": GreenhouseScraper,
}


async def run(sites: list[str], query: str, location: str, max_pages: int):
    start = time.time()

    print(f"\n{'='*60}")
    print(f"HONG KONG JOB SCRAPER")
    print(f"{'='*60}")
    print(f"Query: {query}")
    print(f"Location: {location}")
    print(f"Sites: {', '.join(sites)}")
    print(f"Pages per site: {max_pages}")
    print()

    async def scrape_site(name):
        try:
            scraper = SCRAPERS[name]()
            return name, await scraper.scrape(query, location, max_pages)
        except Exception as e:
            print(f"  [{name}] FAILED: {e}")
            return name, []

    tasks = [scrape_site(s) for s in sites if s in SCRAPERS]
    results = await asyncio.gather(*tasks)

    all_listings = []
    site_counts = {}
    for name, listings in results:
        all_listings.extend(listings)
        site_counts[name] = len(listings)

    elapsed = time.time() - start

    if not all_listings:
        print("\nNo listings found.")
        return

    # Deduplicate across all sources (URL + title+company + fuzzy)
    unique = deduplicate(all_listings)
    dupes_removed = len(all_listings) - len(unique)

    print(f"\n{'='*60}")
    print(f"DONE in {elapsed:.0f}s")
    for site, count in site_counts.items():
        desc = sum(1 for l in all_listings if l.source == site and l.description)
        print(f"  {site}: {count} listings ({desc} with descriptions)")
    if dupes_removed:
        print(f"  duplicates removed: {dupes_removed}")
    print(f"  TOTAL unique jobs: {len(unique)}")
    print(f"{'='*60}")
    all_listings = unique

    csv_path = save_results(all_listings, query, location, "combined")
    if csv_path:
        print("\nGenerating Excel report...")
        excel_path = generate_excel(csv_path)

        if excel_path and os.path.exists(excel_path):
            try:
                os.startfile(os.path.abspath(excel_path))
            except Exception:
                pass

    _cleanup_old_files()


def _cleanup_old_files():
    import glob
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
    for ext in ["*.csv", "*.xlsx"]:
        files = sorted(glob.glob(os.path.join(output_dir, ext)), key=os.path.getmtime)
        for f in files[:-2]:
            try:
                os.remove(f)
            except PermissionError:
                pass


def main():
    parser = argparse.ArgumentParser(description="Hong Kong Job Scraper")
    parser.add_argument("--sites", nargs="+", default=["jobspy", "jobsdb", "lever", "greenhouse"],
                        choices=list(SCRAPERS.keys()),
                        help="Sites to scrape (default: jobspy + jobsdb)")
    parser.add_argument("--query", default="data analyst",
                        help="Job search query")
    parser.add_argument("--location", default="Hong Kong",
                        help="Location")
    parser.add_argument("--pages", type=int, default=3,
                        help="Pages per site (default: 3)")

    args = parser.parse_args()
    asyncio.run(run(args.sites, args.query, args.location, args.pages))


if __name__ == "__main__":
    main()
