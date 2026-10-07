# GradGuide: International Student Job Discovery Tool

GradGuide is a job discovery tool for **international students** covering casual, part-time, full-time, and internship roles. Built on a custom web scraper engine with real-time visa work-hour awareness, transparent employer trust signals, and integrated application tracking with follow-up reminders.

![GradGuide Demo Preview](docs/assets/preview.png)

---

## Key Features

1. **Custom Web Scraper Engine:** Uses `requests` + `BeautifulSoup` / JSON-LD schema markup (`JobPosting`). Respects `robots.txt`, enforces delays, and avoids third-party job board APIs or LLM extraction.
2. **Work-Hour Awareness:** Automatically calculates projected fortnightly hours and warns students when a job would breach their student visa cap (e.g. 48 hrs/fortnight in Australia).
3. **Employer Trust Signals:** Evaluates postings using transparent, deterministic red-flag rules (sub-minimum wage pay, cash-in-hand phrasing, upfront application fees, anonymous hirers).
4. **Application Tracker & Reminders:** Provides full application lifecycle tracking (`saved`, `applied`, `interview`, `offer`) with automated follow-up reminder banners.

---

## Quick Start Guide

### 1. Requirements & Setup
- Python 3.11+
- Node.js 18+

```bash
# Clone repository and create virtual environment
python -m venv .venv
# On Windows PowerShell:
.venv\Scripts\Activate.ps1

# Install Python dependencies
pip install -r requirements.txt
```

### 2. Seed Database (Offline Fixture Mode)
```bash
python -m db.seed
```

### 3. Run FastAPI Backend & Frontend
```bash
# Run FastAPI Backend (Serves static React frontend on http://localhost:8000)
uvicorn api.main:app --reload --port 8000
```

### 4. Run Scraper CLI
```bash
# Offline fixture scrape:
python -m scraper.run --offline

# Live scrape (respects robots.txt, delays, and an optional city filter):
python -m scraper.run --city Melbourne
```

### 5. Run Test Suite
```bash
pytest
```

---

## Project Documentation Links
- [Architecture & Dataflow Diagram](docs/ARCHITECTURE.md)
- [Source Spike & Evaluation Matrix](docs/SOURCES.md)
- [Detailed Technical Write-up](docs/WRITEUP.md)
- [Interview & Project Defense Prep](docs/INTERVIEW_PREP.md)
- [Demo Video Script](docs/VIDEO_SCRIPT.md)
- [Design Decisions Log](docs/DECISIONS.md)

---

## License & Compliance Note
Visa rules and minimum wage rates are configuration-driven (`config/visa_rules.yaml`, `config/pay_rules.yaml`) and verified against official government sources (*Department of Home Affairs* & *Fair Work Ombudsman*). All guidance provided by GradGuide is decision support, not legal advice.
