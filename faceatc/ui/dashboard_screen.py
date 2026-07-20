import tkinter as tk
from tkinter import ttk, messagebox


def build(app):
    frame = tk.Frame(app.root)
    frame.pack(pady=20)

    tk.Label(frame, text="Dashboard", font=("Arial", 18)).pack(pady=10)

    def go(module_name):
        import importlib
        module = importlib.import_module(f"ui.{module_name}")
        app.show(module)

    def logout():
        if messagebox.askyesno("Logout", "Are you sure you want to log out?"):
            from ui import login_screen
            app.show(login_screen)

    ttk.Button(frame, text="Add Student", width=25, command=lambda: go("add_student_screen")).pack(pady=5)
    ttk.Button(frame, text="Remove Student", width=25, command=lambda: go("remove_student_screen")).pack(pady=5)
    ttk.Button(frame, text="Mark Attendance", width=25, command=lambda: go("mark_attendance_screen")).pack(pady=5)
    ttk.Button(frame, text="View Attendance", width=25, command=lambda: go("view_attendance_screen")).pack(pady=5)
    ttk.Button(frame, text="Generate Report", width=25, command=lambda: go("report_screen")).pack(pady=5)
    ttk.Button(frame, text="Logout", width=25, command=logout).pack(pady=5)
