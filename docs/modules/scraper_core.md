# Scraper Core Module Explainer (`scraper_core`)

## Overview
The `scraper_core` module provides polite HTTP fetching, HTML caching, Schema.org `JobPosting` JSON-LD parsing, and the abstract `BaseScraper` contract.

## Key Files & Classes

1. **`scraper/fetcher.py` (`Fetcher`)**
   - **User-Agent:** Identifies the project as `GradGuideStudentJobTool/0.1 (educational project)`.
   - **Rate Limiting:** Enforces configurable delays between requests (default 1.5 seconds).
   - **Robots.txt:** Parses and respects `robots.txt` per host using `urllib.robotparser`.
   - **Retries & Backoff:** Retries 429/5xx status codes with exponential backoff up to 3 attempts.
   - **Disk Cache:** Saves raw HTML to `data/raw/<host>/<timestamp>_<hash>.html`.
   - **Offline Mode:** Allows tests and local demo runs to load directly from local fixtures without touching live networks.

2. **`scraper/jsonld.py` (`extract_jobposting_jsonld`, `map_jsonld_to_raw_job`)**
   - Parses `<script type="application/ld+json">` elements.
   - Traverses `@graph` structures and lists to isolate Schema.org `JobPosting` objects.
   - Converts JSON-LD structure into unnormalized `RawJob` dictionaries.

3. **`scraper/base.py` (`BaseScraper`, `RawJob`, `ScrapeResult`)**
   - Abstract contract defining `list_urls()`, `parse_listing()`, `parse_detail()`, and `run()`.
   - `run()` orchestrates listing iteration and error collection so scraper failures on single pages don't crash execution.
