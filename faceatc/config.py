"""
Central configuration for FaceATC.
Change paths, camera source, courses, and lectures here — nowhere else.
"""
import os

# --- Paths ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_PATH = os.path.join(DATA_DIR, "students.db")
IMAGE_DIR = os.path.join(DATA_DIR, "images")
EMBEDDING_DIR = os.path.join(DATA_DIR, "embeddings")
LOG_DIR = os.path.join(BASE_DIR, "logs")
LOG_PATH = os.path.join(LOG_DIR, "app.log")
REPORT_DIR = os.path.join(BASE_DIR, "reports", "generated")

# --- Camera ---
# Use 0 for the default laptop webcam, or set FACEATC_CAMERA_URL env var
# to an IP-camera stream URL (e.g. "https://192.168.0.4:8080/video").
CAMERA_SOURCE = os.environ.get("FACEATC_CAMERA_URL", 0)

# --- Face recognition ---
VERIFY_MODEL = "Facenet512"
DETECTOR_BACKEND = "opencv"          # fast; swap to "retinaface" for higher accuracy
MATCH_THRESHOLD = 0.40                # cosine distance; lower = stricter match
FACE_ENFORCE_DETECTION = False        # don't hard-fail if a face isn't clearly detected

# --- Academic structure ---
COURSES = ("BCA", "BSc", "BBA")

LECTURES = {
    "BCA": ["C Programming", "Operating System", "DBMS", "Web Technologies"],
    "BSc": ["Computer Network", "Java", "Software Engineering", "Mathematical Foundation"],
    "BBA": ["Human Resources", "Accounting", "Principle of Management", "Marketing"],
}

# --- Admin auth ---
# SHA-256 hash of the admin password. Default below corresponds to "admin123".
# Generate your own with:
#   python -c "import hashlib; print(hashlib.sha256(b'yourpassword').hexdigest())"
ADMIN_USERNAME = os.environ.get("FACEATC_ADMIN_USER", "admin")
ADMIN_PASSWORD_HASH = os.environ.get(
    "FACEATC_ADMIN_HASH",
    "240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9",  # "admin123"
    # "240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a",  # "admin123"
)


def ensure_dirs():
    """create directories if they dont exist"""
    for path in (DATA_DIR, IMAGE_DIR, EMBEDDING_DIR, LOG_DIR, REPORT_DIR):
        os.makedirs(path, exist_ok=True)
