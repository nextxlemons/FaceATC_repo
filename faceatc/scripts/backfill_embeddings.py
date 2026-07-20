"""
One-time migration script: if you're moving from the old (pairwise-verify)
version of FaceATC and already have students in the database with image_path
set, run this once to generate cached embeddings for all of them.

Usage:
    python scripts/backfill_embeddings.py
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db import initialize_db
from face.embeddings import backfill_embeddings_from_db

if __name__ == "__main__":
    initialize_db()
    done, failed = backfill_embeddings_from_db()
    print(f"Backfill complete — {done} embeddings created, {failed} failed (see logs/app.log).")
