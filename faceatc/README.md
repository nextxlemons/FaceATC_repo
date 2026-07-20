# FaceATC — Face Recognition Attendance System

Restructured, modular version of the original single-file prototype.

## What changed from the original version

- **Modular structure** — database, face recognition, UI, and reports are separate packages instead of one 400-line script.
- **Fast face matching** — face embeddings are computed once at registration and cached to `data/embeddings/*.npy`. Matching a captured face is now one embedding extraction + cheap vector comparisons, instead of re-running `DeepFace.verify()` against every stored photo every time.
- **No hardcoded paths** — everything lives under `config.py`. No more `D:\code grams\...`.
- **Background threading** — face matching runs off the Tkinter main thread, so the camera preview doesn't freeze during recognition.
- **Real logging** — errors are logged to `logs/app.log` instead of being silently swallowed.
- **Hashed admin password** — no more plaintext `"a"/"a"` comparison.
- **Working report export** — CSV always available; PDF available if `reportlab` is installed.
- **Safe camera lifecycle** — `Camera` class as a context manager, so the webcam always releases even if an error occurs.

## Setup

```bash
pip install -r requirements.txt
python main.py
```

Default admin login: username `admin`, password `admin123` (change via `FACEATC_ADMIN_USER` / `FACEATC_ADMIN_HASH` env vars — see `config.py` for how to generate a new hash).

## Migrating from the old version

If you already have students registered in `students.db` from the old script:

1. Copy your old `students.db` into `data/students.db`.
2. Copy your old student images into `data/images/<course>/<student_id>.jpg` (matching the `image_path` column, or update the DB rows to point at the new location).
3. Run the backfill script once to generate cached embeddings for everyone:
   ```bash
   python scripts/backfill_embeddings.py
   ```

## Project layout

```
faceatc/
├── main.py                  # entry point
├── config.py                 # paths, courses, lectures, camera, thresholds
├── auth.py                    # admin login (hashed password)
├── logger.py                  # logging setup
├── database/                  # SQLite schema + repositories
├── face/                      # camera, embeddings, matching
├── ui/                         # one file per screen
├── reports/                    # CSV/PDF export
└── scripts/                    # one-time migration utilities
```

## Notes / things you may want to tune

- `config.MATCH_THRESHOLD` (cosine distance, default `0.40`) controls how strict face matching is — lower it if you're getting false positives, raise it if real matches are being rejected. Test with your own dataset.
- `config.CAMERA_SOURCE` defaults to `0` (default webcam). Set the `FACEATC_CAMERA_URL` environment variable to use an IP camera stream instead.
- PDF export needs `reportlab` (`pip install reportlab`) — CSV export works with no extra dependencies.
