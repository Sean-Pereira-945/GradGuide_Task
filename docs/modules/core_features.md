# Core Features Explainer (`core_features`)

## Overview
This module implements the **three required original features** designed for international student job discovery:

1. **Work-Hour Awareness (`pipeline/visa.py`)**
   - Checks job hours against student visa fortnightly caps (e.g. 48 hrs/fortnight in Australia).
   - Accounts for current student weekly commitments and semester breaks (unlimited work allowed).
   - Returns clear status bands (`ok`, `warning`, `over_cap`, `unknown_hours`) and plain-English explanations with government URL citations.

2. **Employer Trust Signals (`pipeline/trust.py`)**
   - Rules-based red-flag evaluation engine.
   - Audits postings for:
     - Sub-minimum wage rates (checked against Fair Work Ombudsman rates)
     - Cash-in-hand / off-the-books phrasing
     - Upfront applicant training/application fees
     - Confidential/unlisted employers
     - Upfront sensitive document requests (passport/bank info)
   - Outputs transparent 0–100 trust scores (`low_risk`, `check_carefully`, `high_risk`) with itemized reasons.

3. **Application Tracker with Reminders (`api/routes_tracker.py`)**
   - Full CRUD lifecycle management for student job applications (`saved`, `applied`, `interview`, `offer`, `rejected`).
   - Automated follow-up reminder alerts via `/api/applications/reminders`.
