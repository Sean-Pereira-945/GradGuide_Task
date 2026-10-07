"""Visa Work-Hour Awareness pipeline module."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class VisaCheckResult:
    status: str  # ok | warning | over_cap | unknown_hours
    current_weekly_hours: float
    job_weekly_hours: Optional[float]
    projected_fortnightly_hours: float
    fortnightly_cap: float
    explanation: str
    official_source_url: str


def check_visa_work_hours(
    job_hours_max: Optional[float],
    current_weekly_hours: float = 0.0,
    in_study_period: bool = True,
    fortnightly_cap: float = 48.0,
    official_source_url: str = "https://immi.homeaffairs.gov.au",
) -> VisaCheckResult:
    """Check if adding a job's weekly hours breaches the student visa fortnightly cap."""

    # Unlimited work during semester breaks
    if not in_study_period:
        return VisaCheckResult(
            status="ok",
            current_weekly_hours=current_weekly_hours,
            job_weekly_hours=job_hours_max,
            projected_fortnightly_hours=(current_weekly_hours + (job_hours_max or 0)) * 2,
            fortnightly_cap=fortnightly_cap,
            explanation="Unlimited work hours allowed during official study breaks.",
            official_source_url=official_source_url,
        )

    if job_hours_max is None:
        return VisaCheckResult(
            status="unknown_hours",
            current_weekly_hours=current_weekly_hours,
            job_weekly_hours=None,
            projected_fortnightly_hours=current_weekly_hours * 2,
            fortnightly_cap=fortnightly_cap,
            explanation="This job does not specify exact weekly hours. Monitor your schedule carefully.",
            official_source_url=official_source_url,
        )

    total_weekly = current_weekly_hours + job_hours_max
    projected_fortnightly = total_weekly * 2

    if projected_fortnightly > fortnightly_cap:
        explanation = (
            f"Adding ~{job_hours_max:.1f} hrs/week to your current {current_weekly_hours:.1f} hrs/week "
            f"totals {projected_fortnightly:.1f} hrs/fortnight, which EXCEEDS your visa cap of {fortnightly_cap:.0f} hrs/fortnight."
        )
        return VisaCheckResult(
            status="over_cap",
            current_weekly_hours=current_weekly_hours,
            job_weekly_hours=job_hours_max,
            projected_fortnightly_hours=projected_fortnightly,
            fortnightly_cap=fortnightly_cap,
            explanation=explanation,
            official_source_url=official_source_url,
        )
    elif projected_fortnightly >= (fortnightly_cap - 4):
        explanation = (
            f"Adding ~{job_hours_max:.1f} hrs/week brings your total to {projected_fortnightly:.1f} hrs/fortnight, "
            f"nearing your {fortnightly_cap:.0f} hrs limit."
        )
        return VisaCheckResult(
            status="warning",
            current_weekly_hours=current_weekly_hours,
            job_weekly_hours=job_hours_max,
            projected_fortnightly_hours=projected_fortnightly,
            fortnightly_cap=fortnightly_cap,
            explanation=explanation,
            official_source_url=official_source_url,
        )
    else:
        explanation = (
            f"Total projected work ({projected_fortnightly:.1f} hrs/fortnight) is within your "
            f"student visa work cap of {fortnightly_cap:.0f} hrs/fortnight."
        )
        return VisaCheckResult(
            status="ok",
            current_weekly_hours=current_weekly_hours,
            job_weekly_hours=job_hours_max,
            projected_fortnightly_hours=projected_fortnightly,
            fortnightly_cap=fortnightly_cap,
            explanation=explanation,
            official_source_url=official_source_url,
        )
