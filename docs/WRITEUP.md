# WRITEUP.md: GradGuide International Student Job Discovery Tool

## 1. Overview & Problem Statement
International students seeking part-time, casual, or internship work face unique hurdles:
1. **Visa Work-Hour Caps:** Exceeding student visa work limits (e.g. 48 hours/fortnight in Australia) risks visa cancellation.
2. **Underpayment & Job Scams:** Students are frequently targeted by underpaid, cash-in-hand, or fee-charging job scams.
3. **Application Fatigue:** Managing multiple applications across casual venues without clear status or follow-up tracking is difficult.

GradGuide solves these challenges by providing a dedicated job discovery platform featuring custom ethical web scraping, real-time visa work-cap calculations, transparent employer trust scoring, and an integrated application tracker with reminder notifications.

---

## 2. Scraping Architecture & Source Selection
- **Custom Scraper Engine (`requests` + `BeautifulSoup` / JSON-LD):** Built strictly without third-party job board APIs or LLM extraction services.
- **Source Governance:** All candidate targets are checked against `robots.txt` and Terms of Service (recorded in `docs/SOURCES.md`).
- **Resilience:** JSON-LD schema markup (`JobPosting`) is prioritized, with fallback to HTML CSS selectors.
- **Politeness:** Custom User-Agent header, host-level rate limiting, exponential backoff retries, and local HTML caching (`data/raw/`).

---

## 3. The Three Original Features

### Feature 1: Work-Hour Awareness
- **How It Works:** Compares the max weekly hours of a job against the student's current commitments and visa subclass rules (`config/visa_rules.yaml`).
- **Calculation:** `(Current Weekly Hours + Job Weekly Hours) * 2 = Projected Fortnightly Hours`.
- **Status Alerts:** `ok`, `warning` (approaching cap), `over_cap` (breaches 48h limit), `unknown_hours`. Unlimited work is accounted for during official semester breaks.

### Feature 2: Employer Trust Signals
- **How It Works:** Evaluates job postings using transparent, deterministic red-flag rules from `config/trust_rules.yaml`.
- **Rules Evaluated:**
  - Hourly rate below Fair Work national minimum wage ($24.10/hr)
  - Phrases indicating "cash in hand" / off-the-books pay
  - Upfront applicant application or training fees
  - Unlisted or confidential employers
  - Requests for sensitive identity documents upfront
- **Output:** Transparent 0–100 trust score (`low_risk`, `check_carefully`, `high_risk`) with itemized reasons.

### Feature 3: Application Tracker with Follow-up Reminders
- **How It Works:** Dedicated SQLite tracking system managing application lifecycle states (`saved`, `applied`, `interview`, `offer`, `rejected`).
- **Reminders:** Automatically schedules a +7 day follow-up check date upon application submit, alerting the student via the `/api/applications/reminders` banner on login.

---

## 4. Verification & Defense Notes
- **No Invented Facts:** Minimum wage and visa rules are cited from official government sources (`Fair Work Ombudsman` & `Department of Home Affairs`).
- **Offline Reliability:** Fully tested with pytest using offline HTML fixtures and seeded SQLite database.
