import tkinter as tk
from tkinter import ttk, messagebox
from auth import verify_admin


def build(app):
    frame = tk.Frame(app.root)
    frame.pack(pady=100)

    tk.Label(frame, text="Admin Login", font=("Arial", 18)).pack(pady=10)
    tk.Label(frame, text="Username:").pack()
    username_entry = tk.Entry(frame)
    username_entry.pack()

    tk.Label(frame, text="Password:").pack()
    password_entry = tk.Entry(frame, show="*")
    password_entry.pack()

    def validate_login():
        username = username_entry.get()
        password = password_entry.get()
        if verify_admin(username, password):
            from ui import dashboard_screen
            app.show(dashboard_screen)
        else:
            messagebox.showerror("Login Failed", "Invalid username or password.")

    password_entry.bind("<Return>", lambda e: validate_login())
    ttk.Button(frame, text="Login", command=validate_login).pack(pady=20)
