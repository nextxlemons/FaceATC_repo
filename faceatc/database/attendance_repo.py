"""
All attendance-table database operations live here.
"""
import datetime
from database.db import get_connection
from database.students_repo import increment_attendance_count
from logger import get_logger

log = get_logger(__name__)


class AlreadyMarkedError(Exception):
    pass


def mark_attendance(student_id: str, course: str, lecture_name: str) -> str:
    """Records attendance for today. Raises AlreadyMarkedError if already marked."""
    date = datetime.datetime.now().strftime("%Y-%m-%d")

    with get_connection() as conn:
        existing = conn.execute(
            '''SELECT 1 FROM attendance
               WHERE student_id = ? AND course = ? AND lecture_name = ? AND date = ?''',
            (student_id, course, lecture_name, date),
        ).fetchone()

        if existing:
            raise AlreadyMarkedError(
                f"Attendance already marked for {student_id} in {course} - {lecture_name} today."
            )

        conn.execute(
            '''INSERT INTO attendance (student_id, course, lecture_name, date)
               VALUES (?, ?, ?, ?)''',
            (student_id, course, lecture_name, date),
        )

    increment_attendance_count(student_id)
    log.info(f"Marked attendance: {student_id} / {course} / {lecture_name} / {date}")
    return date


def get_attendance_for_course(course: str, lecture_name: str = None, date: str = None):
    query = "SELECT * FROM attendance WHERE course = ?"
    params = [course]
    if lecture_name:
        query += " AND lecture_name = ?"
        params.append(lecture_name)
    if date:
        query += " AND date = ?"
        params.append(date)

    with get_connection() as conn:
        return conn.execute(query, params).fetchall()


def get_all_attendance():
    with get_connection() as conn:
        return conn.execute("SELECT * FROM attendance ORDER BY date DESC").fetchall()
