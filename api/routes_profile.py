"""Student profile endpoints."""

from typing import Optional
from fastapi import APIRouter
from pydantic import BaseModel
from db.database import get_connection

router = APIRouter(prefix="/api/profile", tags=["profile"])


class ProfileUpdate(BaseModel):
    country: Optional[str] = "Australia"
    visa_type: Optional[str] = "Student (Subclass 500)"
    current_weekly_hours: Optional[float] = 0.0
    in_study_period: Optional[bool] = True
    home_city: Optional[str] = "Adelaide"


@router.get("")
def get_profile():
    sql = "SELECT * FROM student_profile WHERE id = 1"
    with get_connection() as conn:
        row = conn.execute(sql).fetchone()

    if not row:
        return {
            "country": "Australia",
            "visa_type": "Student (Subclass 500)",
            "current_weekly_hours": 12.0,
            "in_study_period": True,
            "home_city": "Adelaide",
        }

    data = dict(row)
    data["in_study_period"] = bool(data.get("in_study_period", 1))
    return data


@router.put("")
def update_profile(profile: ProfileUpdate):
    sql = """
    UPDATE student_profile
    SET country = ?, visa_type = ?, current_weekly_hours = ?, in_study_period = ?, home_city = ?
    WHERE id = 1;
    """
    with get_connection() as conn:
        conn.execute(
            sql,
            (
                profile.country,
                profile.visa_type,
                profile.current_weekly_hours,
                1 if profile.in_study_period else 0,
                profile.home_city,
            ),
        )
        conn.commit()

    return {"message": "Profile updated successfully"}
