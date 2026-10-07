"""Database helper functions for SQLite operations."""

import json
import os
import sqlite3
from typing import Any, Optional

DEFAULT_DB_PATH = "data/jobs.db"


def get_connection(db_path: str = DEFAULT_DB_PATH) -> sqlite3.Connection:
    """Open SQLite connection and enforce foreign keys."""
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_db(db_path: str = DEFAULT_DB_PATH, schema_path: str = "db/schema.sql") -> None:
    """Initialize database tables from schema SQL file."""
    if not os.path.exists(schema_path):
        raise FileNotFoundError(f"Schema file not found at {schema_path}")

    with open(schema_path, "r", encoding="utf-8") as f:
        schema_sql = f.read()

    with get_connection(db_path) as conn:
        conn.executescript(schema_sql)
        conn.commit()


def upsert_job(job_dict: dict[str, Any], db_path: str = DEFAULT_DB_PATH) -> bool:
    """Upsert a normalized job record into the database idempotently."""
    sql = """
    INSERT INTO jobs (
        id, source, url, title, employer, location_text, city, lat, lng,
        job_type, category, pay_min, pay_max, pay_unit, pay_text,
        hours_min, hours_max, posted_date, description, content_hash,
        trust_score, trust_reasons, first_seen, last_seen
    ) VALUES (
        :id, :source, :url, :title, :employer, :location_text, :city, :lat, :lng,
        :job_type, :category, :pay_min, :pay_max, :pay_unit, :pay_text,
        :hours_min, :hours_max, :posted_date, :description, :content_hash,
        :trust_score, :trust_reasons, :first_seen, :last_seen
    )
    ON CONFLICT(content_hash) DO UPDATE SET
        last_seen = excluded.last_seen,
        url = excluded.url,
        pay_text = excluded.pay_text,
        trust_score = excluded.trust_score,
        trust_reasons = excluded.trust_reasons;
    """

    # Ensure JSON serializable trust_reasons
    params = dict(job_dict)
    if isinstance(params.get("trust_reasons"), list):
        params["trust_reasons"] = json.dumps(params["trust_reasons"])

    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(sql, params)
        conn.commit()
        return cursor.rowcount > 0
