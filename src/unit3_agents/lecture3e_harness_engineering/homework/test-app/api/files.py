import os
from pathlib import Path

from flask import Blueprint, request, jsonify, send_from_directory, abort
from werkzeug.utils import secure_filename

from auth.middleware import login_required
from config import UPLOAD_DIR, MAX_UPLOAD_SIZE

files_bp = Blueprint("files", __name__, url_prefix="/files")

ALLOWED_EXTENSIONS = {".txt", ".pdf", ".png", ".jpg", ".jpeg", ".gif"}


def _allowed(filename):
    return Path(filename).suffix.lower() in ALLOWED_EXTENSIONS


@files_bp.route("/upload", methods=["POST"])
@login_required
def upload():
    """Upload a file to the user's personal directory."""
    f = request.files.get("file")
    if f is None or f.filename == "":
        return jsonify({"error": "No file provided"}), 400

    if not _allowed(f.filename):
        return jsonify({"error": "File type not allowed"}), 400

    safe_name = secure_filename(f.filename)
    user_dir = os.path.join(UPLOAD_DIR, str(request.current_user["id"]))
    os.makedirs(user_dir, exist_ok=True)
    f.save(os.path.join(user_dir, safe_name))
    return jsonify({"message": "Uploaded", "filename": safe_name}), 201


@files_bp.route("/download", methods=["GET"])
@login_required
def download():
    """Download a file from the shared uploads directory."""
    filename = request.args.get("name", "")
    subdir = request.args.get("dir", "")

    # Build the target path from user-supplied directory and filename
    base = Path(UPLOAD_DIR)
    target = base / subdir / filename

    if not target.exists():
        abort(404)

    return send_from_directory(str(target.parent), target.name)
