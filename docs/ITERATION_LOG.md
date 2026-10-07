# Iteration log

## 2026-10-04 — React frontend scaffold

### Changed

- Updated the frontend decision in [PLAN.md](../PLAN.md) from plain HTML/CSS/JS to React + Vite.
- Added the initial repository ignore rules and documentation baseline.
- Added a Vite React application under `frontend/`.
- Added a responsive, keyboard-visible preview surface with search state and empty-state handling.

### Validation

- `npm install` completed successfully with 0 reported vulnerabilities.
- `npm run build` completed successfully with Vite 7.3.6.
- The Vite development server responded with HTTP 200 at `http://localhost:5173`.
- Browser smoke test confirmed the page renders and the search field filters the two preview rows.

### Deferred

- FastAPI, SQLite, scraper modules, and Python requirements.
- Live job sources and all visa/wage values.
- API integration and persistent application tracking.

## 2026-10-04 — Python/FastAPI scaffold

### Changed

- Added pinned Python dependencies in [requirements.txt](../requirements.txt).
- Added the planned `api/`, `scraper/`, `pipeline/`, `db/`, `config/`, and `tests/` boundaries.
- Added a minimal FastAPI app with `GET /api/health`.
- Added empty, explicitly unverified configuration files for sources, visa rules, wages, and trust rules.
- Added a backend module explainer and a passing API smoke test.

### Validation

- `pip install -r requirements.txt` completed successfully in `.venv`.
- `pytest tests\test_scaffold.py -q` passed: 1 test.
- `npm run build` passed again for the React frontend.
- The FastAPI app exposes `/api/health`, `/docs`, and the generated OpenAPI routes.

### Deferred

- Source approval and raw HTML fixtures.
- Database schema implementation and seeded demo data.
- Job, profile, tracker, and scraper API routes.
