"""Application tracking endpoints (CRUD + Follow-up Reminders)."""

from datetime import datetime, date
from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from db.database import get_connection

router = APIRouter(prefix="/api/applications", tags=["applications"])


class ApplicationCreate(BaseModel):
    job_id: str
    status: str = "saved"  # saved | applied | interview | offer | rejected
    applied_on: Optional[str] = None
    follow_up_on: Optional[str] = None
    notes: Optional[str] = ""


class ApplicationUpdate(BaseModel):
    status: Optional[str] = None
    applied_on: Optional[str] = None
    follow_up_on: Optional[str] = None
    notes: Optional[str] = None


@router.get("")
def list_applications():
    sql = """
    SELECT a.*, j.title, j.employer, j.location_text, j.pay_text, j.job_type
    FROM applications a
    JOIN jobs j ON a.job_id = j.id
    ORDER BY a.updated_at DESC;
    """
    with get_connection() as conn:
        rows = conn.execute(sql).fetchall()

    return {"data": [dict(r) for r in rows]}


@router.post("")
def create_application(app: ApplicationCreate):
    now = datetime.now().isoformat()
    sql = """
    INSERT INTO applications (job_id, status, applied_on, follow_up_on, notes, created_at, updated_at)
    VALUES (?, ?, ?, ?, ?, ?, ?);
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(sql, (app.job_id, app.status, app.applied_on, app.follow_up_on, app.notes, now, now))
        conn.commit()
        app_id = cursor.lastrowid

    return {"id": app_id, "message": "Application tracked successfully"}


@router.patch("/{app_id}")
def update_application(app_id: int, app: ApplicationUpdate):
    now = datetime.now().isoformat()
    fields = []
    params = []

    if app.status is not None:
        fields.append("status = ?")
        params.append(app.status)
    if app.applied_on is not None:
        fields.append("applied_on = ?")
        params.append(app.applied_on)
    if app.follow_up_on is not None:
        fields.append("follow_up_on = ?")
        params.append(app.follow_up_on)
    if app.notes is not None:
        fields.append("notes = ?")
        params.append(app.notes)

    if not fields:
        raise HTTPException(status_code=400, detail="No fields provided for update")

    fields.append("updated_at = ?")
    params.append(now)
    params.append(app_id)

    sql = f"UPDATE applications SET {', '.join(fields)} WHERE id = ?"
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(sql, params)
        conn.commit()

        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Application record not found")

    return {"message": "Application updated successfully"}


@router.delete("/{app_id}")
def delete_application(app_id: int):
    sql = "DELETE FROM applications WHERE id = ?"
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(sql, [app_id])
        conn.commit()

        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Application record not found")

    return {"message": "Application tracking record removed"}


@router.get("/reminders")
def get_due_reminders():
    today_str = date.today().isoformat()
    sql = """
    SELECT a.*, j.title, j.employer
    FROM applications a
    JOIN jobs j ON a.job_id = j.id
    WHERE a.follow_up_on IS NOT NULL AND a.follow_up_on <= ? AND a.status IN ('saved', 'applied', 'interview')
    ORDER BY a.follow_up_on ASC;
    """
    with get_connection() as conn:
        rows = conn.execute(sql, [today_str]).fetchall()

    return {"due_reminders": [dict(r) for r in rows]}
