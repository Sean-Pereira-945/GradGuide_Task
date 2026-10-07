"""Smoke tests for the initial project boundary."""

from fastapi.testclient import TestClient

from api.main import app


def test_health_endpoint() -> None:
    """The API should expose a predictable local readiness check."""

    response = TestClient(app).get("/api/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "GradGuide Job Discovery API"}
