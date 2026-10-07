# VIDEO_SCRIPT.md: Demo Video Presentation Script (3-5 Minutes)

## 0:00 - 0:45 | Introduction & Problem
- "Hello, this is GradGuide, an international student job discovery tool built for casual, part-time, full-time, and internship roles."
- "International students face unique challenges: strict student visa work-hour caps, underpaid or scam job postings, and tracking multiple casual applications."

## 0:45 - 1:45 | Live Demonstration of Features
- **Job Discovery & Filters:** Demonstrate filtering by job type (casual/part-time), category, and city.
- **Feature 1 (Visa Work-Hour Awareness):** Show the live badge on a job card warning when a 20-hour role pushes a student with 12 current weekly hours over their 48-hour fortnightly cap.
- **Feature 2 (Employer Trust Signals):** Open job drawer and review the trust score breakdown and red-flag reasons.
- **Feature 3 (Application Tracker & Reminders):** Save a job, mark as applied, and highlight the follow-up reminder notification banner.

## 1:45 - 3:30 | Technical Code Walkthrough
- **Scraper Engine:** Walk through `scraper/fetcher.py` showing `robots.txt` checks, delay enforcement, and offline fixture fallback. Show `scraper/jsonld.py` extracting Schema.org markup.
- **Normalization Pipeline:** Explain `pipeline/normalize.py` parsing pay rates and dates, and `pipeline/dedupe.py` generating deterministic content hashes.
- **Rules Engines:** Walk through `pipeline/visa.py` and `pipeline/trust.py` demonstrating how rules live in YAML config files (`config/visa_rules.yaml`, `config/trust_rules.yaml`).

## 3:30 - 4:00 | Conclusion & Testing Strategy
- Show running `pytest` with all 14 tests passing.
- Highlight compliance: no job-board APIs, no LLM calls in the data pipeline, and zero invented facts.
