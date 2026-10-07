"""API unit tests for job search, application tracking, and profile routes."""

import pytest
from fastapi.testclient import TestClient
from api.main import app
from db.seed import seed_database

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_temp_db(tmp_path, monkeypatch):
    test_db = str(tmp_path / "test_jobs.db")
    monkeypatch.setattr("db.database.DEFAULT_DB_PATH", test_db)
    monkeypatch.setattr("api.routes_jobs.get_connection", lambda: __import__("db.database").database.get_connection(test_db))
    monkeypatch.setattr("api.routes_tracker.get_connection", lambda: __import__("db.database").database.get_connection(test_db))
    monkeypatch.setattr("api.routes_profile.get_connection", lambda: __import__("db.database").database.get_connection(test_db))

    seed_database(db_path=test_db)


def test_health_check():
    res = client.get("/api/health")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"


def test_jobs_search_endpoint():
    res = client.get("/api/jobs")
    assert res.status_code == 200
    body = res.json()
    assert "data" in body
    assert len(body["data"]) > 0


def test_profile_get_and_update():
    get_res = client.get("/api/profile")
    assert get_res.status_code == 200
    assert get_res.json()["country"] == "Australia"

    put_res = client.put("/api/profile", json={"current_weekly_hours": 16.0, "in_study_period": True})
    assert put_res.status_code == 200

    get_updated = client.get("/api/profile")
    assert get_updated.json()["current_weekly_hours"] == 16.0


def test_applications_crud():
    # First get a job ID
    jobs_res = client.get("/api/jobs").json()
    job_id = jobs_res["data"][0]["id"]

    # Create tracking record
    create_res = client.post(
        "/api/applications",
        json={"job_id": job_id, "status": "applied", "applied_on": "2026-10-05", "follow_up_on": "2026-10-12"},
    )
    assert create_res.status_code == 200
    app_id = create_res.json()["id"]

    # List applications
    list_res = client.get("/api/applications")
    assert list_res.status_code == 200
    assert len(list_res.json()["data"]) == 1

    # Delete tracking record
    del_res = client.delete(f"/api/applications/{app_id}")
    assert del_res.status_code == 200
