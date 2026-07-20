import tkinter as tk
from tkinter import ttk, messagebox
from database.students_repo import remove_student
from logger import get_logger

log = get_logger(__name__)


def build(app):
    frame = tk.Frame(app.root)
    frame.pack(pady=50)

    tk.Label(frame, text="Remove Student", font=("Arial", 18)).pack(pady=10)
    tk.Label(frame, text="Student ID:").pack()
    student_id_entry = tk.Entry(frame)
    student_id_entry.pack()

    def do_remove():
        sid = student_id_entry.get().strip()
        if not sid:
            messagebox.showerror("Error", "Please enter a valid Student ID.")
            return
        try:
            remove_student(sid)
            messagebox.showinfo("Success", f"Student {sid} removed successfully!")
            student_id_entry.delete(0, tk.END)
        except ValueError as e:
            messagebox.showerror("Error", str(e))
        except Exception as e:
            log.exception("Failed to remove student")
            messagebox.showerror("Error", f"An unexpected error occurred: {e}")

    ttk.Button(frame, text="Remove Student", command=do_remove).pack(pady=5)

    from ui import dashboard_screen
    ttk.Button(frame, text="Go Back", command=lambda: app.show(dashboard_screen)).pack(pady=5)
