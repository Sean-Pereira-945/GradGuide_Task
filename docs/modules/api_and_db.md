# API & Storage Module Explainer (`api_and_db`)

## Overview
The `api_and_db` module manages SQLite persistence, offline database seeding, and RESTful API endpoints for job search, student profile management, and job application tracking.

## Key Components

1. **`db/schema.sql` & `db/database.py`**
   - SQLite tables: `jobs`, `scrape_runs`, `applications`, `student_profile`.
   - Idempotent upserts on `content_hash` to ensure clean incremental scraping.

2. **`db/seed.py`**
   - Offline database seeder loading listings from test HTML fixtures using offline scrapers.

3. **`api/main.py` & Routes (`routes_jobs.py`, `routes_tracker.py`, `routes_profile.py`)**
   - `GET /api/jobs`: Search & filtering (keyword, job type, category, city, min pay, trust score, pagination).
   - `GET /api/jobs/{id}`: Detail job record retrieval.
   - `GET / PUT /api/profile`: Student profile management (weekly hours, visa details, study period).
   - `GET / POST / PATCH / DELETE /api/applications`: Job application tracking & status management.
   - `GET /api/applications/reminders`: Follow-up date notification reminders.
