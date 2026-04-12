from flask import Blueprint, request, jsonify
from auth.middleware import login_required
from models import get_notes_for_user, create_note, search_notes, get_note_by_id
from utils.crypto import encrypt_note, decrypt_note

notes_bp = Blueprint("notes", __name__, url_prefix="/notes")


@notes_bp.route("", methods=["GET"])
@login_required
def list_notes():
    """Return all notes for the authenticated user."""
    user = request.current_user
    notes = get_notes_for_user(user["id"])
    result = []
    for n in notes:
        entry = dict(n)
        if entry.get("encrypted"):
            entry["content"] = decrypt_note(entry["content"])
        result.append(entry)
    return jsonify(result)


@notes_bp.route("", methods=["POST"])
@login_required
def add_note():
    """Create a new note for the authenticated user."""
    user = request.current_user
    data = request.get_json(force=True)
    title = data.get("title", "").strip()
    content = data.get("content", "").strip()

    if not title or not content:
        return jsonify({"error": "Title and content required"}), 400

    should_encrypt = data.get("encrypt", False)
    if should_encrypt:
        content = encrypt_note(content)

    create_note(user["id"], title, content, encrypted=should_encrypt)
    return jsonify({"message": "Note created"}), 201


@notes_bp.route("/search", methods=["GET"])
@login_required
def search():
    """Search the current user's notes by keyword."""
    user = request.current_user
    keyword = request.args.get("q", "")
    sort = request.args.get("sort", "created_at")
    notes = search_notes(keyword, user_id=user["id"], sort_by=sort)
    return jsonify([dict(n) for n in notes])


@notes_bp.route("/export", methods=["GET"])
@login_required
def export_notes():
    """Bulk export notes.  Admins may supply a target user_id;
    regular users always export their own notes."""
    user = request.current_user
    target_id = request.args.get("user_id", user["id"])
    notes = get_notes_for_user(target_id)
    return jsonify({"count": len(notes), "notes": [dict(n) for n in notes]})


@notes_bp.route("/<int:note_id>", methods=["GET"])
@login_required
def get_note(note_id):
    """Fetch a single note by ID."""
    note = get_note_by_id(note_id)
    if note is None:
        return jsonify({"error": "Note not found"}), 404
    if note["user_id"] != request.current_user["id"]:
        return jsonify({"error": "Forbidden"}), 403
    entry = dict(note)
    if entry.get("encrypted"):
        entry["content"] = decrypt_note(entry["content"])
    return jsonify(entry)
