# Architecture

## Current scaffold

```mermaid
flowchart LR
  A[React + Vite frontend] --> B[Static build assets]
  B -. future production serving .-> C[FastAPI]
  C -. future data access .-> D[(SQLite)]
```

The frontend is intentionally independent of the backend during this first iteration. The initial React shell uses local placeholder state only; API calls will be introduced after the FastAPI routes and seeded database exist.

## Target data flow

```mermaid
flowchart LR
  A[Source sites] --> B[Fetcher: robots, delay, cache]
  B --> C[Site parsers: JSON-LD + CSS]
  C --> D[Normalize: pay, date, type, hours]
  D --> E[Dedupe + trust rules]
  E --> F[(SQLite)]
  F --> G[FastAPI]
  G --> H[React web UI]
```

The scraper and rules engine remain server-side. The UI should display transparent results from those modules and must not make legal or trust determinations on its own.
