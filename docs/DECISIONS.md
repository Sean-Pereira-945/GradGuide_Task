# Architecture decisions

| Date | Decision | Alternatives considered | Why |
|---|---|---|---|
| 2026-10-04 | Use React with Vite for the frontend, built to static assets for FastAPI to serve in production. | Plain HTML/CSS/JS served directly by FastAPI; a larger React framework. | React gives the listing, detail, profile, and tracker surfaces a maintainable component model without introducing server-rendering complexity. Vite keeps local development and production builds small and explicit. |

## Open decisions

- Confirm the target country before adding visa or wage values.
- Select and verify scraping sources before implementing site-specific parsers.
- Decide whether the development workflow should proxy `/api` through Vite or run the frontend and FastAPI servers separately.
