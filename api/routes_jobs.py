"""Job endpoints for search, filtering, and live scraping trigger."""

import json
from typing import Optional
from fastapi import APIRouter, Query, BackgroundTasks
from db.database import get_connection, upsert_job
from db.seed import seed_database
from scraper.run import run_scrapers
from pipeline.models import Job
from pipeline.normalize import (
    parse_pay,
    parse_hours,
    parse_posted_date,
    classify_job_type,
    classify_category,
    normalize_location,
)
from pipeline.trust import evaluate_job_trust
from pipeline.dedupe import generate_content_hash
from datetime import datetime, date

router = APIRouter(prefix="/api/jobs", tags=["jobs"])


def execute_live_scrape_and_ingest(city: Optional[str] = None):
    """Execute live scrapers across all registered sources and ingest new jobs into SQLite."""
    try:
        raw_jobs = run_scrapers(offline=False, city=city)
        today = date.today()
        now_iso = datetime.now().isoformat()

        for r in raw_jobs:
            min_p, max_p, unit = parse_pay(r.pay_text)
            min_h, max_h = parse_hours(f"{r.description} {r.type_text}")
            posted = parse_posted_date(r.posted_text, today=today)
            jtype = classify_job_type(r.title, r.type_text, r.description)
            cat = classify_category(r.title, r.description)
            city = normalize_location(r.location)
            chash = generate_content_hash(r.employer, r.title, r.location)

            # Evaluate trust signals dynamically
            trust_res = evaluate_job_trust(r.title, r.employer, r.description, min_p, unit)

            job_obj = Job(
                id=chash[:16],
                source=r.source,
                url=r.url,
                title=r.title,
                employer=r.employer,
                location_text=r.location,
                city=city,
                job_type=jtype,
                category=cat,
                pay_min=min_p,
                pay_max=max_p,
                pay_unit=unit,
                pay_text=r.pay_text,
                hours_per_week_min=min_h,
                hours_per_week_max=max_h,
                posted_date=posted,
                description=r.description,
                first_seen=now_iso,
                last_seen=now_iso,
                trust_score=trust_res.score,
                trust_reasons=trust_res.reasons,
                content_hash=chash,
            )

            job_dict = job_obj.model_dump()
            job_dict["posted_date"] = str(job_dict["posted_date"]) if job_dict["posted_date"] else None
            job_dict["first_seen"] = str(job_dict["first_seen"])
            job_dict["last_seen"] = str(job_dict["last_seen"])
            job_dict["hours_min"] = job_dict.pop("hours_per_week_min", None)
            job_dict["hours_max"] = job_dict.pop("hours_per_week_max", None)

            upsert_job(job_dict)
    except Exception as err:
        print(f"Error during live background scrape: {err}")


@router.post("/refresh-live")
def trigger_live_scrape(
    city: Optional[str] = Query(None, description="Only scrape listings in this city")
):
    """Trigger real-time live scrape execution of all configured career sources."""
    execute_live_scrape_and_ingest(city=city)
    city_message = f" in {city}" if city else ""
    return {
        "message": (
            f"Live scrape completed successfully{city_message}. "
            "Latest jobs updated in real time!"
        )
    }


@router.get("")
def search_jobs(
    q: Optional[str] = Query(None, description="Keyword search in title, employer, description"),
    job_type: Optional[str] = Query(None, description="part_time | casual | full_time | internship"),
    category: Optional[str] = Query(None, description="cafe | retail | delivery | tutoring | tech | other"),
    city: Optional[str] = Query(None, description="Adelaide | Melbourne | Sydney etc."),
    min_pay: Optional[float] = Query(None, description="Minimum pay threshold"),
    min_trust: Optional[int] = Query(None, description="Minimum trust score threshold (0-100)"),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=50),
):
    sql = "SELECT * FROM jobs WHERE 1=1"
    params = []

    if q:
        sql += " AND (title LIKE ? OR employer LIKE ? OR description LIKE ?)"
        pattern = f"%{q}%"
        params.extend([pattern, pattern, pattern])

    if job_type:
        sql += " AND job_type = ?"
        params.append(job_type)

    if category:
        sql += " AND category = ?"
        params.append(category)

    if city:
        sql += " AND city = ?"
        params.append(city)

    if min_pay is not None:
        sql += " AND (pay_min >= ? OR pay_max >= ?)"
        params.extend([min_pay, min_pay])

    if min_trust is not None:
        sql += " AND trust_score >= ?"
        params.append(min_trust)

    # Count total matching records
    count_sql = f"SELECT COUNT(*) FROM ({sql})"
    with get_connection() as conn:
        total = conn.execute(count_sql, params).fetchone()[0]

        # Add pagination
        sql += " ORDER BY posted_date DESC LIMIT ? OFFSET ?"
        offset = (page - 1) * limit
        params.extend([limit, offset])

        rows = conn.execute(sql, params).fetchall()

    jobs = []
    for r in rows:
        item = dict(r)
        if item.get("trust_reasons"):
            try:
                item["trust_reasons"] = json.loads(item["trust_reasons"])
            except Exception:
                item["trust_reasons"] = []
        jobs.append(item)

    return {
        "data": jobs,
        "pagination": {
            "total": total,
            "page": page,
            "limit": limit,
            "total_pages": (total + limit - 1) // limit if limit else 1,
        },
    }


@router.get("/{job_id}")
def get_job_detail(job_id: str):
    sql = "SELECT * FROM jobs WHERE id = ?"
    with get_connection() as conn:
        row = conn.execute(sql, [job_id]).fetchone()

    if not row:
        return {"error": "Job not found"}, 404

    item = dict(row)
    if item.get("trust_reasons"):
        try:
            item["trust_reasons"] = json.loads(item["trust_reasons"])
        except Exception:
            item["trust_reasons"] = []

    return item
