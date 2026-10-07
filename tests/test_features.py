"""Unit tests for Phase 8 features: Visa work hours, trust engine, and application reminders."""

from pipeline.models import PayUnit
from pipeline.visa import check_visa_work_hours
from pipeline.trust import evaluate_job_trust


def test_visa_work_hour_checks():
    # Scenario 1: Under cap
    res_ok = check_visa_work_hours(job_hours_max=5.0, current_weekly_hours=8.0)
    assert res_ok.status == "ok"
    assert res_ok.projected_fortnightly_hours == 26.0

    # Scenario 2: Exceeding cap (16 current + 10 job = 26/wk -> 52/fortnight > 48)
    res_over = check_visa_work_hours(job_hours_max=10.0, current_weekly_hours=16.0)
    assert res_over.status == "over_cap"
    assert res_over.projected_fortnightly_hours == 52.0

    # Scenario 3: Semester break (unlimited)
    res_break = check_visa_work_hours(job_hours_max=30.0, current_weekly_hours=20.0, in_study_period=False)
    assert res_break.status == "ok"

    # Scenario 4: Unknown hours
    res_unknown = check_visa_work_hours(job_hours_max=None, current_weekly_hours=12.0)
    assert res_unknown.status == "unknown_hours"


def test_trust_signals_engine():
    # Clean listing
    clean_res = evaluate_job_trust(
        title="Student Library Assistant",
        employer="Adelaide Uni",
        description="Assisting at desk",
        pay_min=31.50,
        pay_unit=PayUnit.HOUR,
    )
    assert clean_res.score == 100
    assert clean_res.band == "low_risk"

    # Under minimum wage flag
    underpaid_res = evaluate_job_trust(
        title="Waitstaff",
        employer="Local Diner",
        description="Serving tables",
        pay_min=18.00,
        pay_unit=PayUnit.HOUR,
        min_wage_hourly=24.10,
    )
    assert underpaid_res.score < 80
    assert any("below Fair Work national minimum wage" in r for r in underpaid_res.reasons)

    # Scam flag (training fee)
    fee_res = evaluate_job_trust(
        title="Data Entry Assistant",
        employer="Online Corp",
        description="Must pay upfront training fee of $150.",
        pay_min=30.00,
        pay_unit=PayUnit.HOUR,
    )
    assert fee_res.score <= 50
    assert any("upfront fees" in r for r in fee_res.reasons)
