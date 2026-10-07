# Backend scaffold

## What it does

`api/main.py` creates the first FastAPI application boundary and exposes `GET /api/health`. The remaining package directories establish the module boundaries for scrapers, normalization, rules, and SQLite storage.

## Why this shape

The planned system has a server-side scraping and rules pipeline behind an HTTP API. Creating the boundary first allows the React frontend and backend to be developed independently while keeping the eventual route structure explicit.

## Key files

- `requirements.txt` pins the planned Python dependencies.
- `api/main.py` defines the application object and local health check.
- `config/` holds data-driven rules and intentionally contains no unverified country values.
- `tests/test_scaffold.py` protects the initial API contract.

## Deliberate limitations

This iteration does not fetch live pages, create a database, or expose job routes. Those behaviors require source approval and verified configuration values.
