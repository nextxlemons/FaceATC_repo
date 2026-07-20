"""
Root application window and screen-switching controller.
Each screen is a class with .show(app) that builds its widgets into app.root.
"""
import tkinter as tk
from ttkbootstrap import Style


class App:
    def __init__(self):
        self.root = tk.Tk()
        self.style = Style(theme="flatly")
        self.root.title("FaceATC — Face Recognition Attendance System")
        self.root.geometry("1000x650")
        self.current_screen = None

    def clear(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def show(self, screen_module):
        """screen_module must expose a build(app) function."""
        self.clear()
        self.current_screen = screen_module
        screen_module.build(self)

    def run(self):
        self.root.mainloop()
