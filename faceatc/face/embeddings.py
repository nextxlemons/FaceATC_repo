"""
Face embedding extraction and caching.

Instead of calling DeepFace.verify() pairwise against every stored image
(slow — re-runs detection + inference every single time), we compute a
numeric embedding for each student ONCE at registration time and cache it
to disk. Matching a new face then only requires ONE embedding extraction
(for the captured frame) plus cheap vector comparisons.
"""
import os
import numpy as np
from deepface import DeepFace
from config import EMBEDDING_DIR, VERIFY_MODEL, DETECTOR_BACKEND, FACE_ENFORCE_DETECTION
from logger import get_logger

log = get_logger(__name__)


class FaceNotDetectedError(Exception):
    pass


def compute_embedding(image_path: str) -> np.ndarray:
    """Extract a face embedding vector from an image file."""
    try:
        result = DeepFace.represent(
            img_path=image_path,
            model_name=VERIFY_MODEL,
            detector_backend=DETECTOR_BACKEND,
            enforce_detection=FACE_ENFORCE_DETECTION,
        )
    except Exception as e:
        log.exception(f"Face detection failed for {image_path}")
        raise FaceNotDetectedError(str(e)) from e

    if not result:
        raise FaceNotDetectedError("No face detected in image.")

    return np.array(result[0]["embedding"])


def _embedding_path(student_id: str) -> str:
    os.makedirs(EMBEDDING_DIR, exist_ok=True)
    return os.path.join(EMBEDDING_DIR, f"{student_id}.npy")


def save_embedding(student_id: str, embedding: np.ndarray):
    np.save(_embedding_path(student_id), embedding)
    log.info(f"Saved embedding for {student_id}")


def load_embedding(student_id: str) -> np.ndarray:
    path = _embedding_path(student_id)
    if not os.path.exists(path):
        raise FileNotFoundError(f"No cached embedding for student {student_id}")
    return np.load(path)


def delete_embedding(student_id: str):
    path = _embedding_path(student_id)
    if os.path.exists(path):
        os.remove(path)
        log.info(f"Deleted embedding for {student_id}")


def load_all_embeddings(student_ids: list) -> dict:
    """Load cached embeddings for a list of student IDs, skipping any that are missing."""
    embeddings = {}
    for sid in student_ids:
        try:
            embeddings[sid] = load_embedding(sid)
        except FileNotFoundError:
            log.warning(f"Missing embedding for student {sid} — skipping (re-register to fix)")
    return embeddings


def register_face(student_id: str, image_path: str) -> np.ndarray:
    """Compute and cache the embedding for a newly registered student's photo."""
    embedding = compute_embedding(image_path)
    save_embedding(student_id, embedding)
    return embedding


def backfill_embeddings_from_db():
    """
    One-time utility: for any student in the DB without a cached embedding
    (e.g. migrating from the old verify-pairwise version), compute it now
    from their stored image_path.
    """
    from database.students_repo import get_all_students

    students = get_all_students()
    done, failed = 0, 0
    for student in students:
        sid = student["student_id"]
        if os.path.exists(_embedding_path(sid)):
            continue
        try:
            register_face(sid, student["image_path"])
            done += 1
        except FaceNotDetectedError:
            log.warning(f"Could not backfill embedding for {sid}: no face detected")
            failed += 1
    log.info(f"Backfill complete: {done} embeddings created, {failed} failed")
    return done, failed
