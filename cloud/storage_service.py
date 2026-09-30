"""
Cloud Object Storage Service (abstraction layer)
==================================================
Handles FILES (images, exported plans) as opposed to structured records,
which live in database_service.py. This is the difference between a cloud
DATABASE (structured rows/documents) and cloud OBJECT STORAGE (raw files).

Local/free-tier implementation: files are written to a local folder that
plays the role of a storage bucket. Swapping to a real cloud provider later
only requires re-implementing the three functions below (save_file,
read_file, delete_file) against, e.g., Firebase Storage or an S3 bucket —
nothing else in the app needs to change.
"""

import os
import re
import uuid

STORAGE_ROOT = os.environ.get(
    "STORAGE_ROOT", os.path.join(os.path.dirname(__file__), "..", "data", "storage_bucket")
)

ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".pdf", ".txt", ".json"}
MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024  # 5 MB demo cap


def _safe_filename(filename: str) -> str:
    filename = os.path.basename(filename)
    filename = re.sub(r"[^A-Za-z0-9_.-]", "_", filename)
    return filename or "file"


def _user_dir(user_id: str) -> str:
    path = os.path.join(STORAGE_ROOT, user_id)
    os.makedirs(path, exist_ok=True)
    return path


def validate_file(filename: str, size_bytes: int):
    ext = os.path.splitext(filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ValueError(f"File type '{ext}' is not allowed for this demo bucket.")
    if size_bytes > MAX_FILE_SIZE_BYTES:
        raise ValueError("File exceeds the 5 MB demo size limit.")


def save_file(user_id: str, filename: str, file_bytes: bytes) -> dict:
    """Save bytes under this user's namespace in the storage bucket.
    Returns the storage_path to persist in the database record."""
    validate_file(filename, len(file_bytes))
    safe_name = _safe_filename(filename)
    unique_name = f"{uuid.uuid4().hex[:8]}_{safe_name}"
    full_path = os.path.join(_user_dir(user_id), unique_name)
    with open(full_path, "wb") as f:
        f.write(file_bytes)
    # storage_path is relative, mirroring a bucket object key (not tied to
    # the local machine's absolute path) so it stays portable to real cloud storage.
    storage_path = f"{user_id}/{unique_name}"
    return {"storage_path": storage_path, "size_bytes": len(file_bytes)}


def read_file(storage_path: str) -> bytes:
    full_path = os.path.join(STORAGE_ROOT, storage_path)
    if not os.path.abspath(full_path).startswith(os.path.abspath(STORAGE_ROOT)):
        raise ValueError("Invalid storage path.")
    with open(full_path, "rb") as f:
        return f.read()


def delete_file(storage_path: str) -> bool:
    full_path = os.path.join(STORAGE_ROOT, storage_path)
    if not os.path.abspath(full_path).startswith(os.path.abspath(STORAGE_ROOT)):
        raise ValueError("Invalid storage path.")
    if os.path.exists(full_path):
        os.remove(full_path)
        return True
    return False
