"""Unit tests for normalization pipeline (pay, date, hours, job type, dedupe)."""

from datetime import date, timedelta
from pipeline.models import JobType, PayUnit
from pipeline.normalize import (
    parse_pay,
    parse_hours,
    parse_posted_date,
    classify_job_type,
    classify_category,
    normalize_location,
)
from pipeline.dedupe import generate_content_hash


def test_parse_pay():
    min_p, max_p, unit = parse_pay("$31.50 per hour")
    assert min_p == 31.50
    assert max_p == 31.50
    assert unit == PayUnit.HOUR

    min_p, max_p, unit = parse_pay("$28.50 - $32.00 / hr")
    assert min_p == 28.50
    assert max_p == 32.00
    assert unit == PayUnit.HOUR

    min_p, max_p, unit = parse_pay("$65,000 p.a.")
    assert min_p == 65000.0
    assert unit == PayUnit.YEAR


def test_parse_hours():
    min_h, max_h = parse_hours("Maximum 15 hours per week during semester.")
    assert min_h is None
    assert max_h == 15.0

    min_h, max_h = parse_hours("12-18 hours per week")
    assert min_h == 12.0
    assert max_h == 18.0


def test_parse_posted_date():
    today = date(2026, 10, 5)
    assert parse_posted_date("Posted 2 days ago", today=today) == date(2026, 10, 3)
    assert parse_posted_date("Posted 1 day ago", today=today) == date(2026, 10, 4)
    assert parse_posted_date("Posted yesterday", today=today) == date(2026, 10, 4)
    assert parse_posted_date("2026-10-01", today=today) == date(2026, 10, 1)


def test_classify_job_type_and_category():
    jtype = classify_job_type("Student Library Assistant", "Casual", "Helpdesk role")
    assert jtype == JobType.CASUAL

    cat = classify_category("Campus Cafe Barista", "Make coffee")
    assert cat == "cafe"


def test_dedupe_hash():
    hash1 = generate_content_hash("Woolworths", "Team Member", "Melbourne")
    hash2 = generate_content_hash("woolworths ", "team member", "melbourne")
    assert hash1 == hash2
