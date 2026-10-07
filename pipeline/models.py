"""Pydantic data models for standardized job entities."""

from datetime import date, datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class JobType(str, Enum):
    PART_TIME = "part_time"
    CASUAL = "casual"
    FULL_TIME = "full_time"
    INTERNSHIP = "internship"
    UNKNOWN = "unknown"


class PayUnit(str, Enum):
    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    YEAR = "year"
    UNKNOWN = "unknown"


class Job(BaseModel):
    id: str
    source: str
    url: str
    title: str
    employer: Optional[str] = None
    location_text: Optional[str] = None
    city: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    job_type: JobType = JobType.UNKNOWN
    category: Optional[str] = "other"
    pay_min: Optional[float] = None
    pay_max: Optional[float] = None
    pay_unit: PayUnit = PayUnit.UNKNOWN
    pay_text: Optional[str] = None
    hours_per_week_min: Optional[float] = None
    hours_per_week_max: Optional[float] = None
    posted_date: Optional[date] = None
    description: str = ""
    first_seen: datetime = Field(default_factory=datetime.now)
    last_seen: datetime = Field(default_factory=datetime.now)
    trust_score: int = 100
    trust_reasons: list[str] = Field(default_factory=list)
    content_hash: str
