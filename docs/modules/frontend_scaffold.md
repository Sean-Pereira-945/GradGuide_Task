# React frontend scaffold

## What it does

`frontend/src/App.jsx` establishes the first application surface for GradGuide. It provides a product header, a search control, a small sample listing area, and an explicit empty-state note explaining that live listings arrive in a later phase.

## Why React + Vite

The planned product has several related surfaces: searchable listings, a detail drawer, a student profile, and an application tracker. React gives those surfaces reusable components and local state without coupling the UI to FastAPI's server-rendering concerns. Vite provides a small development server and produces static assets that FastAPI can serve in production.

## Key files

- `frontend/src/main.jsx` mounts the React tree.
- `frontend/src/App.jsx` owns the initial page composition and temporary local state.
- `frontend/src/styles.css` contains the first responsive visual foundation.
- `frontend/vite.config.js` defines the build tool boundary.

## Deliberate limitations

The sample listing is clearly labeled as preview content and is not sourced from a live site. API calls, authentication, and persistent state are intentionally deferred until the backend contract is implemented.
