from flask import Blueprint, jsonify, request

from cloud import database_service as db
from cloud import storage_service as storage
from backend.utils.auth_utils import require_auth

file_bp = Blueprint("files", __name__)


@file_bp.post("/upload")
@require_auth
def upload_file(user_id):
    if "file" not in request.files:
        return jsonify({"error": "No file part named 'file' in the request."}), 400
    uploaded = request.files["file"]
    if uploaded.filename == "":
        return jsonify({"error": "No file selected."}), 400

    file_bytes = uploaded.read()
    try:
        result = storage.save_file(user_id, uploaded.filename, file_bytes)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    file_id = db.create_file_record(
        user_id=user_id,
        filename=uploaded.filename,
        storage_path=result["storage_path"],
        content_type=uploaded.content_type,
        size_bytes=result["size_bytes"],
    )
    return jsonify({"message": "File uploaded.", "file_id": file_id}), 201


@file_bp.get("/files")
@require_auth
def list_files(user_id):
    return jsonify({"files": db.list_files(user_id)}), 200


@file_bp.get("/files/<file_id>")
@require_auth
def get_file(user_id, file_id):
    record = db.get_file(user_id, file_id)
    if not record:
        return jsonify({"error": "File not found."}), 404
    try:
        content = storage.read_file(record["storage_path"])
    except (ValueError, FileNotFoundError):
        return jsonify({"error": "File content missing from storage bucket."}), 404

    import base64

    return jsonify({
        "file_id": record["file_id"],
        "filename": record["filename"],
        "content_type": record["content_type"],
        "size_bytes": record["size_bytes"],
        "data_base64": base64.b64encode(content).decode("utf-8"),
    }), 200


@file_bp.delete("/files/<file_id>")
@require_auth
def delete_file(user_id, file_id):
    record = db.get_file(user_id, file_id)
    if not record:
        return jsonify({"error": "File not found."}), 404
    storage.delete_file(record["storage_path"])
    db.delete_file_record(user_id, file_id)
    return jsonify({"message": "File deleted."}), 200
