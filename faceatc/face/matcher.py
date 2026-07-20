"""
Cheap embedding comparison — no repeated model inference.
Once embeddings are extracted (see embeddings.py), matching is just
vector math, so this scales to hundreds of students without slowing down.
"""
import numpy as np
from config import MATCH_THRESHOLD


def cosine_distance(a: np.ndarray, b: np.ndarray) -> float:
    return 1 - (np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


def find_best_match(captured_embedding: np.ndarray, known_embeddings: dict,
                     threshold: float = MATCH_THRESHOLD):
    """
    Compare a captured face embedding against a dict of {student_id: embedding}.
    Returns (student_id, distance) for the best match under the threshold,
    or (None, best_distance) if nothing matched closely enough.
    """
    best_id, best_dist = None, float("inf")

    for student_id, known_embedding in known_embeddings.items():
        dist = cosine_distance(captured_embedding, known_embedding)
        if dist < best_dist:
            best_id, best_dist = student_id, dist

    if best_dist < threshold:
        return best_id, best_dist
    return None, best_dist


def is_duplicate_face(captured_embedding: np.ndarray, known_embeddings: dict,
                       threshold: float = MATCH_THRESHOLD):
    """Used during registration to check if this face is already enrolled."""
    match_id, dist = find_best_match(captured_embedding, known_embeddings, threshold)
    return match_id is not None, match_id, dist
