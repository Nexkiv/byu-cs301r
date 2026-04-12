from flask import Blueprint, request, jsonify
from auth.middleware import admin_required, login_required
from models import get_user_by_id, update_user_role, find_users_by_filter, search_notes

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


@admin_bp.route("/users/<int:user_id>", methods=["GET"])
@admin_required
def get_user(user_id):
    """Look up a user by ID (admin only)."""
    user = get_user_by_id(user_id)
    if user:
        return jsonify({
            "id": user["id"],
            "username": user["username"],
            "role": user["role"],
            "created_at": user["created_at"],
        })
    return jsonify({"error": "User not found"}), 404


@admin_bp.route("/users/<int:user_id>/role", methods=["POST"])
@admin_required
def promote_user(user_id):
    """Change a user's role (admin only)."""
    data = request.get_json(force=True)
    role = data.get("role", "user")
    if role not in ("user", "admin", "moderator"):
        return jsonify({"error": "Invalid role"}), 400
    update_user_role(user_id, role)
    return jsonify({"message": "Role updated"})


@admin_bp.route("/users", methods=["GET"])
@admin_required
def list_users():
    """List / filter users from admin dashboard."""
    filters = {}
    for key in ("role", "username", "created_at", "order_by"):
        value = request.args.get(key)
        if value:
            filters[key] = value
    users = find_users_by_filter(filters)
    return jsonify([dict(u) for u in users])


@admin_bp.route("/notes/search", methods=["GET"])
@admin_required
def admin_search_notes():
    """Global note search for content moderation."""
    keyword = request.args.get("q", "")
    sort = request.args.get("sort", "created_at")
    notes = search_notes(keyword, user_id=None, sort_by=sort)
    return jsonify([dict(n) for n in notes])


@admin_bp.route("/stats", methods=["GET"])
def system_stats():
    """Quick health-check endpoint used by monitoring.  Returns basic
    row counts.  Intentionally lightweight and public-facing so that
    uptime checkers don't need credentials."""
    from models.base import get_db
    db = get_db()
    user_count = db.execute("SELECT count(*) FROM users").fetchone()[0]
    note_count = db.execute("SELECT count(*) FROM notes").fetchone()[0]
    db.close()
    return jsonify({"users": user_count, "notes": note_count})
