import threading
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import cv2

from config import COURSES, LECTURES, CAMERA_SOURCE
from face.camera import Camera
from face.embeddings import compute_embedding, load_all_embeddings, FaceNotDetectedError
from face.matcher import find_best_match
from database.students_repo import get_students_by_course
from database.attendance_repo import mark_attendance, AlreadyMarkedError
from logger import get_logger

log = get_logger(__name__)


def build(app):
    frame = tk.Frame(app.root)
    frame.pack(pady=30)

    tk.Label(frame, text="Mark Attendance", font=("Arial", 18)).pack(pady=10)

    tk.Label(frame, text="Select Course:").pack()
    course_var = tk.StringVar()
    course_box = ttk.Combobox(frame, textvariable=course_var, state="readonly", values=COURSES)
    course_box.pack()

    tk.Label(frame, text="Select Lecture:").pack()
    lecture_var = tk.StringVar()
    lecture_box = ttk.Combobox(frame, textvariable=lecture_var, state="readonly")
    lecture_box.pack()

    def update_lectures(*_):
        lecture_box["values"] = LECTURES.get(course_var.get(), [])
        lecture_var.set("")

    course_box.bind("<<ComboboxSelected>>", update_lectures)

    camera_label = tk.Label(frame)
    camera_label.pack(pady=20)
    status_label = tk.Label(frame, text="", fg="blue")
    status_label.pack()

    camera = Camera(CAMERA_SOURCE)
    stop_preview = {"flag": False}

    def start_camera():
        try:
            camera.open()
        except RuntimeError as e:
            messagebox.showerror("Camera Error", str(e))
            return
        update_frame()

    def update_frame():
        if stop_preview["flag"]:
            return
        ret, frame_img = camera.read()
        if ret:
            rgb = cv2.cvtColor(frame_img, cv2.COLOR_BGR2RGB)
            imgtk = ImageTk.PhotoImage(image=Image.fromarray(rgb))
            camera_label.imgtk = imgtk
            camera_label.configure(image=imgtk)
        if camera.is_opened():
            camera_label.after(15, update_frame)

    def go_back():
        stop_preview["flag"] = True
        camera.release()
        from ui import dashboard_screen
        app.show(dashboard_screen)

    def capture_and_mark():
        course = course_var.get()
        lecture = lecture_var.get()
        if not course or not lecture:
            messagebox.showerror("Error", "Please select a course and lecture.")
            return

        ret, frame_img = camera.read()
        if not ret:
            messagebox.showerror("Error", "Failed to capture image.")
            return

        capture_btn.config(state="disabled")
        status_label.config(text="Matching face — please wait...")
        threading.Thread(
            target=_process_attendance,
            args=(app, frame_img, course, lecture, status_label, capture_btn),
            daemon=True,
        ).start()

    capture_btn = ttk.Button(frame, text="Capture and Mark Attendance", command=capture_and_mark)
    capture_btn.pack(pady=10)
    ttk.Button(frame, text="Go Back", command=go_back).pack(pady=5)

    start_camera()


def _process_attendance(app, frame_img, course, lecture, status_label, capture_btn):
    temp_path = "temp_attendance.jpg"
    cv2.imwrite(temp_path, frame_img)

    try:
        try:
            captured_embedding = compute_embedding(temp_path)
        except FaceNotDetectedError:
            app.root.after(0, lambda: messagebox.showerror("Error", "No face detected — try again."))
            return

        students = get_students_by_course(course)
        known_embeddings = load_all_embeddings([s["student_id"] for s in students])

        if not known_embeddings:
            app.root.after(0, lambda: messagebox.showwarning(
                "No Data", f"No registered faces found for {course}."
            ))
            return

        match_id, dist = find_best_match(captured_embedding, known_embeddings)

        if match_id is None:
            app.root.after(0, lambda: messagebox.showerror(
                "No Match", f"No matching student found (closest distance: {dist:.3f})."
            ))
            return

        try:
            date = mark_attendance(match_id, course, lecture)
            app.root.after(0, lambda: messagebox.showinfo(
                "Success", f"Attendance marked for {match_id} in {course} - {lecture} ({date})"
            ))
        except AlreadyMarkedError as e:
            app.root.after(0, lambda: messagebox.showinfo("Already Marked", str(e)))

    except Exception as e:
        log.exception("Attendance marking failed")
        app.root.after(0, lambda: messagebox.showerror("Error", f"An unexpected error occurred: {e}"))
    finally:
        import os
        if os.path.exists(temp_path):
            os.remove(temp_path)
        app.root.after(0, lambda: (
            status_label.config(text=""),
            capture_btn.config(state="normal"),
        ))
