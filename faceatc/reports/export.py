"""
Attendance report generation — CSV (always available) and PDF (if reportlab installed).
"""
import csv
import os
import datetime
from config import REPORT_DIR, ensure_dirs
from database.attendance_repo import get_all_attendance, get_attendance_for_course
from logger import get_logger

log = get_logger(__name__)


def export_attendance_csv(course: str = None, lecture_name: str = None) -> str:
    ensure_dirs()
    rows = (
        get_attendance_for_course(course, lecture_name)
        if course else get_all_attendance()
    )

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"attendance_report_{timestamp}.csv"
    filepath = os.path.join(REPORT_DIR, filename)

    with open(filepath, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Student ID", "Course", "Lecture", "Date"])
        for row in rows:
            writer.writerow([row["student_id"], row["course"], row["lecture_name"], row["date"]])

    log.info(f"Exported CSV report: {filepath}")
    return filepath


def export_attendance_pdf(course: str = None, lecture_name: str = None) -> str:
    """Requires: pip install reportlab"""
    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
    except ImportError:
        raise RuntimeError("reportlab is not installed. Run: pip install reportlab")

    ensure_dirs()
    rows = (
        get_attendance_for_course(course, lecture_name)
        if course else get_all_attendance()
    )

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"attendance_report_{timestamp}.pdf"
    filepath = os.path.join(REPORT_DIR, filename)

    data = [["Student ID", "Course", "Lecture", "Date"]]
    for row in rows:
        data.append([row["student_id"], row["course"], row["lecture_name"], row["date"]])

    doc = SimpleDocTemplate(filepath, pagesize=A4)
    table = Table(data)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2C3E50")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F2F2F2")]),
    ]))
    doc.build([table])

    log.info(f"Exported PDF report: {filepath}")
    return filepath
