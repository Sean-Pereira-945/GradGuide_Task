"""Seed script to populate SQLite database from offline HTML fixtures."""

from datetime import datetime, date
import logging
from db.database import init_db, upsert_job
from pipeline.dedupe import generate_content_hash
from pipeline.models import Job, JobType, PayUnit
from pipeline.normalize import (
    parse_pay,
    parse_hours,
    parse_posted_date,
    classify_job_type,
    classify_category,
    normalize_location,
)
from scraper.run import run_scrapers

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def seed_database(db_path: str = "data/jobs.db"):
    logger.info(f"Initializing database at {db_path}...")
    init_db(db_path)

    logger.info("Running scrapers in offline fixture mode...")
    raw_jobs = run_scrapers(offline=True)

    count = 0
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
            trust_score=100,
            trust_reasons=["Verified employer listing"],
            content_hash=chash,
        )

        job_dict = job_obj.model_dump()
        job_dict["posted_date"] = str(job_dict["posted_date"]) if job_dict["posted_date"] else None
        job_dict["first_seen"] = str(job_dict["first_seen"])
        job_dict["last_seen"] = str(job_dict["last_seen"])
        job_dict["hours_min"] = job_dict.pop("hours_per_week_min", None)
        job_dict["hours_max"] = job_dict.pop("hours_per_week_max", None)

        upsert_job(job_dict, db_path=db_path)
        count += 1

    logger.info(f"Database seeded successfully with {count} offline fixture jobs.")


if __name__ == "__main__":
    seed_database()
