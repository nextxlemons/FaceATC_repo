import tkinter as tk
from tkinter import ttk, messagebox
from config import COURSES
from reports.export import export_attendance_csv, export_attendance_pdf
from logger import get_logger

log = get_logger(__name__)


def build(app):
    frame = tk.Frame(app.root)
    frame.pack(pady=50)

    tk.Label(frame, text="Generate Attendance Report", font=("Arial", 18)).pack(pady=10)

    tk.Label(frame, text="Course (optional — leave blank for all):").pack()
    course_var = tk.StringVar()
    ttk.Combobox(frame, textvariable=course_var, state="readonly",
                 values=("",) + COURSES).pack()

    def do_csv():
        try:
            path = export_attendance_csv(course_var.get() or None)
            messagebox.showinfo("Success", f"CSV report saved to:\n{path}")
        except Exception as e:
            log.exception("CSV export failed")
            messagebox.showerror("Error", str(e))

    def do_pdf():
        try:
            path = export_attendance_pdf(course_var.get() or None)
            messagebox.showinfo("Success", f"PDF report saved to:\n{path}")
        except RuntimeError as e:
            messagebox.showerror("Missing dependency", str(e))
        except Exception as e:
            log.exception("PDF export failed")
            messagebox.showerror("Error", str(e))

    ttk.Button(frame, text="Export as CSV", command=do_csv).pack(pady=5)
    ttk.Button(frame, text="Export as PDF", command=do_pdf).pack(pady=5)

    from ui import dashboard_screen
    ttk.Button(frame, text="Go Back", command=lambda: app.show(dashboard_screen)).pack(pady=10)
