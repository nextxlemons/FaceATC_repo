import tkinter as tk
from tkinter import ttk, messagebox
from database.students_repo import get_all_students
from logger import get_logger

log = get_logger(__name__)


def build(app):
    frame = tk.Frame(app.root)
    frame.pack(pady=30, fill="both", expand=True)

    tk.Label(frame, text="View Attendance", font=("Arial", 18)).pack(pady=10)

    tree = ttk.Treeview(frame, columns=("ID", "Name", "Course", "Attendance"), show="headings")
    for col, label in [("ID", "Student ID"), ("Name", "Name"), ("Course", "Course"), ("Attendance", "Total Attendance")]:
        tree.heading(col, text=label)
    tree.pack(fill="both", expand=True, padx=20)

    try:
        for student in get_all_students():
            tree.insert("", tk.END, values=(
                student["student_id"], student["name"], student["course"], student["total_attendance"]
            ))
    except Exception as e:
        log.exception("Failed to load attendance")
        messagebox.showerror("Error", f"Could not load attendance data: {e}")

    from ui import dashboard_screen
    ttk.Button(frame, text="Go Back", command=lambda: app.show(dashboard_screen)).pack(pady=10)
