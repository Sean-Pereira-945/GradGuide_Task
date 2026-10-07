# INTERVIEW_PREP.md: Project Defense & Q&A Guide

## Likely Interview Questions & Defendable Answers

### Q1: Why did you prioritize JSON-LD over CSS selectors?
> **Answer:** Schema.org `JobPosting` JSON-LD provides structured machine-readable metadata provided directly by site owners. It is far less fragile than CSS selectors, which break whenever a site updates its class names or layout markup. When JSON-LD is absent, our scrapers fall back to explicit, documented CSS selectors.

### Q2: How does your scraper respect site rules and rate limits?
> **Answer:** `scraper/fetcher.py` uses `urllib.robotparser` to inspect `robots.txt` before fetching. It enforces a 1.5-second delay between requests, uses exponential backoff on 429/5xx codes, identifies itself with a transparent custom User-Agent, and caches HTML locally to prevent unnecessary web traffic.

### Q3: How do you handle job deduplication?
> **Answer:** We compute a SHA-256 hash of normalized `(employer, title, location)` string tuples. When re-scraping, SQLite performs an `ON CONFLICT(content_hash) DO UPDATE` to update timestamps (`last_seen`) without creating duplicate job entries.

### Q4: How does the Visa Work-Hour Awareness feature operate?
> **Answer:** The system takes the student's current weekly hours plus the job's max weekly hours, multiplies by 2 to project fortnightly hours, and compares it against `config/visa_rules.yaml` (e.g. 48 hours/fortnight cap for Australian Subclass 500 visas). If the student is on semester break, it permits unlimited hours.

### Q5: How are Employer Trust Signals calculated? Is there AI involved?
> **Answer:** No AI or black-box models are used. It runs transparent, deterministic rules against `config/trust_rules.yaml`. Postings start with a score of 100 and lose points for specific red flags like sub-minimum wage pay, "cash in hand" wording, upfront training fees, or missing employer details. Each deduction attaches a human-readable reason.

### Q6: Why did you choose SQLite without an ORM?
> **Answer:** Plain SQL with parameterized queries makes data operations explicit and transparent. It ensures full explainability without hidden ORM query overhead or magic behaviors during project defense.
