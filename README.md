# FaceATC : Face Recognition Attendance System 📸

A face-recognition-based attendance system built for classrooms — staff mark attendance by pointing a camera at a class, no roll call needed. Built with Python, Tkinter, and DeepFace, and restructured from a single-file prototype into a modular application with fast, cached face matching.

---

## 🚀 Overview

FaceATC lets an admin register students by course with a captured photo, then mark attendance for an entire lecture by simply pointing a webcam (or phone IP camera) at the room. Each captured face is matched against cached face embeddings in real time, attendance is logged per course and lecture, and reports can be exported as CSV or PDF.

---

## 🛠️ Technologies Used

| Layer               | Technology                                  |
|---------------------|-----------------------------------------------|
| GUI                 | Python, Tkinter, ttkbootstrap                  |
| Face Recognition    | DeepFace (Facenet512), OpenCV                  |
| Database            | SQLite                                          |
| Reporting           | csv (built-in), ReportLab (PDF)                |
| Architecture        | Modular desktop app — separate DB, face-matching, and UI layers, each screen swapped into one Tkinter root window |

Face matching is embedding-based rather than pairwise image comparison: each student's face is converted to a numeric vector once at registration and cached to disk, so marking attendance for a full class is one embedding extraction plus fast vector comparisons — not a fresh model run per student.

---

## ✨ Core Features

### 🔐 Admin Login
- Single admin account, password stored as a SHA-256 hash (not plaintext)
- Configurable via environment variables, no code edits needed to change credentials

### 🧑‍🎓 Student Registration
- Add a student by ID, name, and course (BCA / BSc / BBA)
- Captures a live photo via webcam or IP camera
- Face is checked against all already-registered students before saving, so the same person can't be enrolled twice
- Face embedding is computed and cached immediately on registration

### 🗑️ Student Removal
- Remove a student by ID — deletes their DB record, attendance history, stored photo, and cached embedding together

### ✅ Attendance Marking
- Select course and lecture, then capture a frame
- Captured face is matched against cached embeddings for that course only (fast, no per-student model calls)
- Duplicate attendance for the same course/lecture/day is blocked automatically
- Face matching runs on a background thread so the camera preview never freezes

### 📋 View Attendance
- Table view of every registered student with their running total attendance count

### 📊 Report Generation
- Export all attendance (or filtered by course) to CSV
- Optional PDF export (via ReportLab) with a formatted table

---

## 🏗️ System Architecture

```
┌────────────────────────┐
│   Tkinter UI Screens   │
│  login → dashboard →   │
│  add/remove/mark/view  │
└──────────┬─────────────┘
           │
┌──────────▼─────────────┐        ┌──────────────────────┐
│   Face Layer           │        │   Database Layer     │
│  camera.py  (webcam)   │        │  students_repo.py    │
│  embeddings.py (cache) │◄──────►│  attendance_repo.py  │
│  matcher.py  (matching)│        │  db.py (SQLite conn) │
└──────────┬─────────────┘        └──────────┬───────────┘
           │                                  │
           ▼                                  ▼
   data/embeddings/*.npy                data/students.db
```

**Data flow for marking attendance:**
1. Admin selects a course and lecture, camera captures a frame.
2. `face/embeddings.py` extracts one embedding from the captured frame.
3. `face/matcher.py` compares it against cached embeddings for that course's registered students (cosine distance).
4. On a match under the confidence threshold, `database/attendance_repo.py` logs attendance for that student/course/lecture/date, guarding against duplicates for the same day.

---

## 📂 Project Structure

```
faceatc/
├── main.py                    # entry point
├── config.py                  # paths, courses, lectures, camera source, thresholds
├── auth.py                    # admin login (hashed password)
├── logger.py                  # app-wide logging setup
├── database/
│   ├── db.py                  # SQLite connection + schema
│   ├── students_repo.py       # student CRUD
│   └── attendance_repo.py     # attendance CRUD
├── face/
│   ├── camera.py               # safe webcam/IP-cam lifecycle
│   ├── embeddings.py           # extract + cache face embeddings
│   └── matcher.py              # cosine-distance face matching
├── ui/
│   ├── app.py                   # root window + screen switching
│   ├── login_screen.py
│   ├── dashboard_screen.py
│   ├── add_student_screen.py
│   ├── remove_student_screen.py
│   ├── mark_attendance_screen.py
│   ├── view_attendance_screen.py
│   └── report_screen.py
├── reports/
│   └── export.py                # CSV / PDF export
├── scripts/
│   └── backfill_embeddings.py   # one-time migration for existing students
├── data/
│   ├── students.db
│   ├── images/                  # registered student photos, by course
│   └── embeddings/              # cached .npy face embeddings
├── logs/
│   └── app.log
├── requirements.txt
└── README.md
```

---

## ⚡ Quick Start

**Prerequisites:** Python 3.10+, pip, a webcam (or IP camera app on your phone)

```bash
# 1. Clone the repository
git clone https://github.com/nextxlemons/FaceATC.git
cd FaceATC

# 2. Create and activate a virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # macOS/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the app
python main.py
```

Default admin login is `admin` / `admin123` — change it by generating a new SHA-256 hash and setting `FACEATC_ADMIN_HASH` (see `config.py`).

To use a phone as an IP camera instead of a laptop webcam, set the `FACEATC_CAMERA_URL` environment variable to your streaming URL before running.

---

## 🔁 Migrating Existing Students

If you have students already registered from an earlier version of this project:

1. Copy the old `students.db` into `data/`.
2. Copy the old student photos into `data/images/<course>/<student_id>.jpg`.
3. Run the backfill script once to generate cached embeddings for everyone:
   ```bash
   python scripts/backfill_embeddings.py
   ```

---

## 🗺️ Roadmap / Ideas for Later

- Live confidence/distance score shown during attendance marking, not just a match/no-match result
- Multi-face detection per frame, to mark a whole row of students in one capture
- Admin-configurable courses/lectures from within the UI instead of `config.py`
- Export attendance directly to Excel with per-lecture summaries
- Package as a standalone executable (PyInstaller) for non-technical staff to run

---

## 📝 Background

FaceATC started as a single-file Tkinter + DeepFace prototype that re-verified each captured face against every stored student photo on every attempt. It's since been restructured into a modular app with cached face embeddings for fast matching, background threading so the UI stays responsive, and proper logging — while keeping the same core workflow.

---

## 📄 License

This project is currently unlicensed / for personal & portfolio use.
