# Normalization Module Explainer (`normalization`)

## Overview
The `normalization` module transforms raw, unstandardized scraper dictionaries (`RawJob`) into strongly-typed `Job` Pydantic models.

## Key Files & Functions

1. **`pipeline/models.py` (`Job`, `JobType`, `PayUnit`)**
   - Canonical dataclass with validation for salary ranges, job type enums (`casual`, `part_time`, `full_time`, `internship`, `unknown`), trust score, and content hash.

2. **`pipeline/normalize.py`**
   - `parse_pay(text)`: Converts strings like `"$28.50 - $32.00 / hr"` or `"$65,000 p.a."` into min/max floats and unit enums.
   - `parse_hours(text)`: Extracts numerical weekly hour constraints (e.g. `12-18 hours per week`).
   - `parse_posted_date(text)`: Handles relative dates (`2 days ago`, `yesterday`) and fixed ISO dates (`YYYY-MM-DD`).
   - `classify_job_type()` & `classify_category()`: Categorizes job postings using transparent keyword matching.
   - `normalize_location()`: Extracts target Australian cities.

3. **`pipeline/dedupe.py` (`generate_content_hash`)**
   - Generates deterministic SHA-256 hashes of `(employer, title, location)` for idempotent upserts.
