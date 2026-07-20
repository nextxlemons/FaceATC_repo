import os
import threading
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import cv2

from config import COURSES, IMAGE_DIR, CAMERA_SOURCE
from face.camera import Camera
from face.embeddings import register_face, load_all_embeddings, FaceNotDetectedError
from face.matcher import is_duplicate_face
from database.students_repo import add_student, get_all_students, DuplicateStudentError
from logger import get_logger

log = get_logger(__name__)


def build(app):
    frame = tk.Frame(app.root)
    frame.pack(pady=30)

    tk.Label(frame, text="Add Student", font=("Arial", 18)).pack(pady=10)

    tk.Label(frame, text="Student ID:").pack()
    student_id_entry = tk.Entry(frame)
    student_id_entry.pack()
    invalid_id_label = tk.Label(frame, text="", fg="red")
    invalid_id_label.pack(pady=(0, 1))

    tk.Label(frame, text="Name:").pack()
    name_entry = tk.Entry(frame)
    name_entry.pack()

    tk.Label(frame, text="Course:").pack()
    course_var = tk.StringVar()
    course_box = ttk.Combobox(frame, textvariable=course_var, state="readonly", values=COURSES)
    course_box.pack()

    capture_btn = ttk.Button(frame, text="Capture Image", state="disabled")
    capture_btn.pack(pady=5)

    from ui import dashboard_screen
    ttk.Button(frame, text="Go Back", command=lambda: app.show(dashboard_screen)).pack(pady=5)

    def check_fields(*_):
        sid = student_id_entry.get()
        valid = bool(sid and name_entry.get() and course_var.get() and " " not in sid)
        capture_btn.config(state="normal" if valid else "disabled")
        if " " in sid:
            student_id_entry.config(fg="red")
            invalid_id_label.config(text="Invalid ID: no spaces allowed")
        else:
            student_id_entry.config(fg="black")
            invalid_id_label.config(text="")

    student_id_entry.bind("<KeyRelease>", check_fields)
    name_entry.bind("<KeyRelease>", check_fields)
    course_box.bind("<<ComboboxSelected>>", check_fields)

    capture_btn.config(
        command=lambda: _open_capture_view(
            app, student_id_entry.get(), name_entry.get(), course_var.get()
        )
    )


def _open_capture_view(app, student_id, name, course):
    app.clear()
    frame = tk.Frame(app.root)
    frame.pack(pady=30)

    tk.Label(frame, text="Capturing Image", font=("Arial", 18)).pack(pady=10)
    camera_label = tk.Label(frame)
    camera_label.pack(pady=20)
    status_label = tk.Label(frame, text="", fg="blue")
    status_label.pack()

    camera = Camera(CAMERA_SOURCE)
    try:
        camera.open()
    except RuntimeError as e:
        messagebox.showerror("Camera Error", str(e))
        from ui import add_student_screen
        app.show(add_student_screen)
        return

    stop_preview = {"flag": False}

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
        from ui import add_student_screen
        app.show(add_student_screen)

    def capture_and_save():
        capture_btn.config(state="disabled")
        status_label.config(text="Processing — please wait...")
        ret, frame_img = camera.read()
        if not ret:
            messagebox.showerror("Error", "Failed to capture image.")
            status_label.config(text="")
            capture_btn.config(state="normal")
            return

        # Run the heavy face-matching work off the main thread so the UI doesn't freeze
        threading.Thread(target=_process_capture, args=(app, frame_img, student_id, name, course, camera, status_label), daemon=True).start()

    capture_btn = ttk.Button(frame, text="Capture", command=capture_and_save)
    capture_btn.pack(pady=10)
    ttk.Button(frame, text="Go Back", command=go_back).pack(pady=5)

    update_frame()


def _process_capture(app, frame_img, student_id, name, course, camera, status_label):
    temp_path = "temp_capture.jpg"
    cv2.imwrite(temp_path, frame_img)

    try:
        # Check against all currently known embeddings to prevent duplicate registration
        all_students = get_all_students()
        known_embeddings = load_all_embeddings([s["student_id"] for s in all_students])

        from face.embeddings import compute_embedding
        try:
            new_embedding = compute_embedding(temp_path)
        except FaceNotDetectedError:
            app.root.after(0, lambda: messagebox.showerror("Error", "No face detected — try again."))
            return

        duplicate, match_id, dist = is_duplicate_face(new_embedding, known_embeddings)
        if duplicate:
            app.root.after(0, lambda: messagebox.showerror(
                "Error", f"This face is already registered (Student ID: {match_id})."
            ))
            return

        image_path = os.path.join(IMAGE_DIR, course, f"{student_id}.jpg")
        os.makedirs(os.path.dirname(image_path), exist_ok=True)
        cv2.imwrite(image_path, frame_img)

        add_student(student_id, name, course, image_path)
        register_face(student_id, image_path)

        app.root.after(0, lambda: messagebox.showinfo("Success", f"Student {name} added successfully!"))

    except DuplicateStudentError as e:
        app.root.after(0, lambda: messagebox.showerror("Error", str(e)))
    except Exception as e:
        log.exception("Failed to add student")
        app.root.after(0, lambda: messagebox.showerror("Error", f"An unexpected error occurred: {e}"))
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)
        camera.release()

        def back_to_dashboard():
            from ui import dashboard_screen
            app.show(dashboard_screen)

        app.root.after(0, back_to_dashboard)
