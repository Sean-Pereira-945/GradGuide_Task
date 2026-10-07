"""Normalization functions for pay, date, hours, job type, category, and location."""

from datetime import date, timedelta
import re
from typing import Optional, Tuple
from pipeline.models import JobType, PayUnit


def parse_pay(pay_text: str) -> Tuple[Optional[float], Optional[float], PayUnit]:
    """Parse raw pay string into min_pay, max_pay, and unit."""
    if not pay_text:
        return None, None, PayUnit.UNKNOWN

    text = pay_text.lower().replace(",", "").replace("/", " ")

    # Identify unit
    unit = PayUnit.UNKNOWN
    if "hour" in text or "hr" in text or "ph" in text or "p.h" in text:
        unit = PayUnit.HOUR
    elif "year" in text or "annum" in text or "p.a" in text or "pa" in text or "k" in text:
        unit = PayUnit.YEAR
    elif "week" in text or "wk" in text or "pw" in text:
        unit = PayUnit.WEEK
    elif "day" in text or "pd" in text:
        unit = PayUnit.DAY

    # Regex for dollar amounts e.g., $28.50 - $32.00 or $31.50
    matches = re.findall(r"\$?\s*(\d+(?:\.\d{1,2})?)", text)
    if not matches:
        return None, None, unit

    floats = [float(m) for m in matches]
    if len(floats) >= 2:
        return min(floats), max(floats), unit
    elif len(floats) == 1:
        return floats[0], floats[0], unit

    return None, None, unit


def parse_hours(text: str) -> Tuple[Optional[float], Optional[float]]:
    """Extract hours per week range e.g., '12-18 hours per week' or 'up to 20 hrs'."""
    if not text:
        return None, None

    t = text.lower()
    # Match pattern e.g. 12-18 hours or 20 hrs or up to 20 hours
    match_range = re.search(r"(\d+(?:\.\d+)?)\s*(?:-|to)\s*(\d+(?:\.\d+)?)\s*(?:hrs|hours|hr)", t)
    if match_range:
        return float(match_range.group(1)), float(match_range.group(2))

    match_single = re.search(r"(?:max|up to)?\s*(\d+(?:\.\d+)?)\s*(?:hrs|hours|hr)", t)
    if match_single:
        val = float(match_single.group(1))
        return None, val

    return None, None


def parse_posted_date(posted_text: str, today: Optional[date] = None) -> Optional[date]:
    """Parse relative or fixed posted dates e.g. '2 days ago', 'Yesterday', '2026-10-01'."""
    if not posted_text:
        return today or date.today()

    if today is None:
        today = date.today()

    t = posted_text.lower().strip()

    if "today" in t or "just posted" in t:
        return today
    if "yesterday" in t:
        return today - timedelta(days=1)

    match_days = re.search(r"(\d+)\s+day", t)
    if match_days:
        days = int(match_days.group(1))
        return today - timedelta(days=days)

    match_weeks = re.search(r"(\d+)\s+week", t)
    if match_weeks:
        weeks = int(match_weeks.group(1))
        return today - timedelta(weeks=weeks)

    # Try ISO format e.g. 2026-10-01
    match_iso = re.search(r"(\d{4}-\d{2}-\d{2})", t)
    if match_iso:
        try:
            return date.fromisoformat(match_iso.group(1))
        except ValueError:
            pass

    return today


def classify_job_type(title: str, type_text: str, description: str, hint: Optional[str] = None) -> JobType:
    """Classify job type into JobType enum based on title, type text, and description."""
    combined = f"{title} {type_text} {description}".lower()

    if "casual" in combined:
        return JobType.CASUAL
    if "part-time" in combined or "part time" in combined or "parttime" in combined:
        return JobType.PART_TIME
    if "intern" in combined or "internship" in combined or "vacation" in combined:
        return JobType.INTERNSHIP
    if "full-time" in combined or "full time" in combined or "fulltime" in combined:
        return JobType.FULL_TIME

    if hint:
        h = hint.lower()
        if "casual" in h:
            return JobType.CASUAL
        if "part" in h:
            return JobType.PART_TIME
        if "intern" in h:
            return JobType.INTERNSHIP

    return JobType.UNKNOWN


def classify_category(title: str, description: str) -> str:
    """Classify job into category e.g., cafe, retail, delivery, tutoring, tech, other."""
    c = f"{title} {description}".lower()
    if any(k in c for k in ["barista", "cafe", "waiter", "waitstaff", "kitchen", "coffee", "hospitality"]):
        return "cafe"
    if any(k in c for k in ["retail", "supermarket", "checkout", "store", "cashier", "customer service"]):
        return "retail"
    if any(k in c for k in ["delivery", "driver", "rider", "courier"]):
        return "delivery"
    if any(k in c for k in ["tutor", "teaching", "academic", "library"]):
        return "tutoring"
    if any(k in c for k in ["developer", "software", "data", "tech", "it"]):
        return "tech"
    return "other"


def normalize_location(location_text: str) -> Optional[str]:
    """Extract a supported Australian city from a listing location."""
    if not location_text:
        return None
    loc = location_text.lower()
    cities = [
        "adelaide", "melbourne", "sydney", "brisbane", "perth", "canberra",
        "hobart", "darwin", "gold coast", "newcastle", "wollongong",
        "geelong", "townsville", "cairns",
    ]
    for city in cities:
        if city in loc:
            return city.capitalize()
    return None
