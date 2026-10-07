"""CLI runner for executing registered site scrapers."""

import argparse
import logging
import os
import yaml
from scraper.fetcher import Fetcher
from scraper.sources.adelaide_uni import AdelaideUniScraper
from scraper.sources.woolworths import WoolworthsScraper
from scraper.sources.monash_uni import MonashScraper
from scraper.sources.gradconnection import GradConnectionScraper
from scraper.sources.university_jobs import UniversityJobsScraper
from pipeline.normalize import normalize_location

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

SCRAPER_REGISTRY = {
    "adelaide_uni": AdelaideUniScraper,
    "woolworths": WoolworthsScraper,
    "monash_uni": MonashScraper,
    "gradconnection": GradConnectionScraper,
    "university_jobs": UniversityJobsScraper,
}


def load_sources_config(config_path: str = "config/sources.yaml") -> list[dict]:
    if not os.path.exists(config_path):
        logger.error(f"Config file not found: {config_path}")
        return []
    with open(config_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data.get("sources", [])


def run_scrapers(source_name: str = None, offline: bool = False, city: str = None):
    sources = load_sources_config()
    fetcher = Fetcher(offline=offline)
    total_jobs = []
    requested_city = normalize_location(city) if city else None
    if city and not requested_city:
        logger.warning("Unsupported city filter '%s'; no jobs will be returned.", city)
        return total_jobs

    for src_cfg in sources:
        name = src_cfg.get("name")
        if not src_cfg.get("enabled", True):
            continue
        if source_name and name != source_name:
            continue

        scraper_cls = SCRAPER_REGISTRY.get(src_cfg.get("scraper", name))
        if not scraper_cls:
            logger.warning(f"No scraper implementation registered for '{name}'")
            continue

        logger.info(f"Running scraper for '{name}' (offline={offline})...")
        scraper = scraper_cls(fetcher, src_cfg)
        
        fixture_path = f"tests/fixtures/{name}/listing.html" if offline else None
        
        if offline and fixture_path and os.path.exists(fixture_path):
            html = fetcher.fetch(src_cfg.get("base_url"), fixture_path=fixture_path).html
            raw_jobs = scraper.parse_listing(html, src_cfg.get("base_url"))
            filtered_jobs = _filter_jobs_by_city(raw_jobs, requested_city)
            total_jobs.extend(filtered_jobs)
            logger.info(
                f"Offline scrape of '{name}' produced {len(filtered_jobs)} jobs"
                f"{f' for {requested_city}' if requested_city else ''}."
            )
        else:
            res = scraper.run()
            filtered_jobs = _filter_jobs_by_city(res.jobs_found, requested_city)
            total_jobs.extend(filtered_jobs)
            logger.info(
                f"Scrape of '{name}' finished. Scraped {res.urls_scraped} URLs, "
                f"found {len(filtered_jobs)} jobs"
                f"{f' for {requested_city}' if requested_city else ''}. "
                f"Errors: {len(res.errors)}"
            )

    return total_jobs


def _filter_jobs_by_city(jobs, requested_city: str = None):
    """Keep only jobs whose normalized location matches the requested city."""
    if not requested_city:
        return jobs
    return [job for job in jobs if normalize_location(job.location) == requested_city]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="GradGuide Job Scraper CLI")
    parser.add_argument("--source", type=str, help="Specific source name to scrape")
    parser.add_argument("--offline", action="store_true", help="Run in offline mode using saved fixtures")
    parser.add_argument("--city", type=str, help="Only return listings in this city, e.g. Adelaide")
    args = parser.parse_args()

    jobs = run_scrapers(source_name=args.source, offline=args.offline, city=args.city)
    print(f"\nTotal jobs scraped: {len(jobs)}")
    for j in jobs:
        print(f"- [{j.source}] {j.title} | {j.employer} | {j.pay_text} ({j.type_text})")
