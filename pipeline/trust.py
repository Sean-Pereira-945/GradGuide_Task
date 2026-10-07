"""Employer Trust Signals rules engine module."""

from dataclasses import dataclass
from typing import Optional
from pipeline.models import PayUnit


@dataclass
class TrustResult:
    score: int
    band: str  # low_risk | check_carefully | high_risk
    reasons: list[str]


def evaluate_job_trust(
    title: str,
    employer: Optional[str],
    description: str,
    pay_min: Optional[float],
    pay_unit: PayUnit,
    min_wage_hourly: float = 24.10,
) -> TrustResult:
    """Evaluate transparent red-flag rules against a job posting."""
    score = 100
    reasons: list[str] = []

    text = f"{title} {description}".lower()

    # Rule 1: Pay below minimum wage
    if pay_min and pay_unit == PayUnit.HOUR and pay_min < min_wage_hourly:
        score -= 35
        reasons.append(f"Stated pay of ${pay_min:.2f}/hr is below Fair Work national minimum wage (${min_wage_hourly:.2f}/hr).")

    # Rule 2: Cash in hand / off the books
    for kw in ["cash in hand", "cash payment", "off the books"]:
        if kw in text:
            score -= 40
            reasons.append(f"Contains phrase '{kw}', indicating possible tax/award non-compliance.")
            break

    # Rule 3: Upfront fees or deposits
    for kw in ["training fee", "application fee", "pay to apply", "upfront cost", "deposit required"]:
        if kw in text:
            score -= 50
            reasons.append(f"Mentions upfront fees ('{kw}'). Legitimate employers do not charge applicants.")
            break

    # Rule 4: Missing or confidential employer
    if not employer or any(v in employer.lower() for v in ["private", "confidential", "anonymous", "unknown"]):
        score -= 20
        reasons.append("Employer identity is confidential or unlisted.")

    # Rule 5: Upfront sensitive document requests
    for kw in ["send passport", "upfront bank details", "tfn upfront"]:
        if kw in text:
            score -= 30
            reasons.append(f"Requests sensitive document upfront ('{kw}').")
            break

    # Clamp score to 0-100
    score = max(0, min(100, score))

    if score >= 80:
        band = "low_risk"
    elif score >= 50:
        band = "check_carefully"
    else:
        band = "high_risk"

    if not reasons:
        reasons.append("No obvious red flags detected. Verified posting format.")

    return TrustResult(score=score, band=band, reasons=reasons)
