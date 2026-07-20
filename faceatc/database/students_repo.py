"""
All student-table database operations live here.
UI code should never write raw SQL directly — go through this module.
"""
import os
from database.db import get_connection
from logger import get_logger

log = get_logger(__name__)


class DuplicateStudentError(Exception):
    pass


def student_id_exists(student_id: str) -> bool:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT 1 FROM students WHERE student_id = ?", (student_id,)
        ).fetchone()
        return row is not None


def add_student(student_id: str, name: str, course: str, image_path: str):
    if not all([student_id, name, course, image_path]):
        raise ValueError("All fields are required.")

    if student_id_exists(student_id):
        raise DuplicateStudentError(f"Student ID '{student_id}' already exists.")

    with get_connection() as conn:
        conn.execute(
            "INSERT INTO students (student_id, name, course, image_path) VALUES (?, ?, ?, ?)",
            (student_id, name, course, image_path),
        )
    log.info(f"Added student {student_id} ({name}, {course})")


def remove_student(student_id: str):
    with get_connection() as conn:
        row = conn.execute(
            "SELECT image_path FROM students WHERE student_id = ?", (student_id,)
        ).fetchone()

        if row is None:
            raise ValueError("Student ID not found.")

        image_path = row["image_path"]
        conn.execute("DELETE FROM students WHERE student_id = ?", (student_id,))
        conn.execute("DELETE FROM attendance WHERE student_id = ?", (student_id,))

    # Clean up image file outside the DB transaction
    if image_path and os.path.exists(image_path):
        try:
            os.remove(image_path)
        except OSError as e:
            log.warning(f"Could not remove image file {image_path}: {e}")

    # Clean up cached embedding too
    from face.embeddings import delete_embedding
    delete_embedding(student_id)

    log.info(f"Removed student {student_id}")


def get_all_students():
    with get_connection() as conn:
        return conn.execute("SELECT * FROM students").fetchall()


def get_students_by_course(course: str):
    with get_connection() as conn:
        return conn.execute(
            "SELECT * FROM students WHERE course = ?", (course,)
        ).fetchall()


def increment_attendance_count(student_id: str):
    with get_connection() as conn:
        conn.execute(
            "UPDATE students SET total_attendance = total_attendance + 1 WHERE student_id = ?",
            (student_id,),
        )
