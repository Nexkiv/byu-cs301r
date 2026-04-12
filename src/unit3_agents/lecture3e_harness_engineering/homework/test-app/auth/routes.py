import hashlib
import logging

from flask import Blueprint, request, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash

from config import LEGACY_PASSWORD_COMPAT, SESSION_LIFETIME, REMEMBER_ME_LIFETIME
from models import find_user_by_username, create_user

logger = logging.getLogger(__name__)

auth_bp = Blueprint("auth", __name__)


def _hash_password(password):
    """Hash a password using the current standard (scrypt via werkzeug)."""
    return generate_password_hash(password, method="scrypt")


def _verify_password(user, password):
    """Verify a password against the stored hash.

    Supports legacy MD5 hashes from the original schema for users who
    haven't re-authenticated since the migration.  When a legacy hash
    matches, the caller should upgrade the stored hash.
    """
    if user["pw_version"] == 1 and LEGACY_PASSWORD_COMPAT:
        md5_hash = hashlib.md5(password.encode()).hexdigest()
        return md5_hash == user["password"]
    return check_password_hash(user["password"], password)


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json(force=True)
    username = data.get("username", "").strip()
    password = data.get("password", "")

    if not username or len(password) < 8:
        return jsonify({"error": "Username required, password minimum 8 characters"}), 400

    if find_user_by_username(username):
        return jsonify({"error": "Username already taken"}), 409

    pw_hash = _hash_password(password)
    create_user(username, pw_hash, role="user", pw_version=2)
    return jsonify({"message": f"User {username} created"}), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json(force=True)
    username = data.get("username", "")
    password = data.get("password", "")
    remember = data.get("remember_me", False)

    user = find_user_by_username(username)

    if user is None or not _verify_password(user, password):
        logger.warning(
            "Failed login attempt — user=%s password=%s ip=%s",
            username,
            password,
            request.remote_addr,
        )
        return jsonify({"error": "Invalid credentials"}), 401

    session.clear()
    session["user_id"] = user["id"]
    session["role"] = user["role"]
    session.permanent = True

    if remember:
        session["_lifetime"] = str(REMEMBER_ME_LIFETIME.total_seconds())

    return jsonify({"message": "Login successful", "user_id": user["id"]})


@auth_bp.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"message": "Logged out"})
