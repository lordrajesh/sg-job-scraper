"""Shared utilities: delays, user-agent rotation, output saving."""

import os
import random
import asyncio
from datetime import datetime
from pathlib import Path

import pandas as pd
from fake_useragent import UserAgent

from config import MIN_DELAY, MAX_DELAY, OUTPUT_FORMAT


_ua = UserAgent(fallback="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")


def get_random_delay() -> float:
    return random.uniform(MIN_DELAY, MAX_DELAY)


async def async_delay():
    await asyncio.sleep(get_random_delay())


def get_user_agent() -> str:
    return _ua.random


def save_results(listings: list, query: str, location: str, source: str):
    """Save job listings to output/ as CSV or JSON."""
    if not listings:
        print(f"  No results to save for {source}")
        return None

    output_dir = Path(__file__).parent.parent / "output"
    output_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_query = query.replace(" ", "_").lower()[:30]
    safe_location = location.replace(" ", "_").lower()[:20]
    filename = f"{source}_{safe_query}_{safe_location}_{timestamp}"

    rows = [listing.to_dict() for listing in listings]
    df = pd.DataFrame(rows)

    if OUTPUT_FORMAT == "json":
        path = output_dir / f"{filename}.json"
        df.to_json(path, orient="records", force_ascii=False, indent=2)
    else:
        path = output_dir / f"{filename}.csv"
        df.to_csv(path, index=False, encoding="utf-8-sig")

    print(f"  Saved {len(listings)} listings to {path.name}")
    return str(path)
