"""Main FastAPI application entry point serving API routes and static frontend."""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from api.routes_jobs import router as jobs_router
from api.routes_tracker import router as tracker_router
from api.routes_profile import router as profile_router

app = FastAPI(
    title="GradGuide Job Discovery API",
    description="Job discovery, visa work-hour awareness, trust scoring & application tracker for international students.",
    version="0.1.0",
)

# Enable CORS for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
app.include_router(jobs_router)
app.include_router(tracker_router)
app.include_router(profile_router)


@app.get("/api/health")
def health_check():
    return {"status": "ok", "service": "GradGuide Job Discovery API"}


# Mount production frontend static assets if built
frontend_dist = os.path.join(os.path.dirname(__file__), "../frontend/dist")
if os.path.exists(frontend_dist):
    app.mount("/", StaticFiles(directory=frontend_dist, html=True), name="static")
