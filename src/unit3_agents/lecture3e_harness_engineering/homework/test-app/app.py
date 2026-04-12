import logging
import traceback

from flask import Flask, jsonify
from flask_cors import CORS

from config import (
    SECRET_KEY,
    SESSION_LIFETIME,
    CORS_ORIGINS,
    LOG_LEVEL,
    LOG_FILE,
)
from models import init_db
from auth import auth_bp
from api import notes_bp, admin_bp, files_bp

# ---------------------------------------------------------------------------
# Application factory
# ---------------------------------------------------------------------------

app = Flask(__name__)
app.secret_key = SECRET_KEY
app.config["PERMANENT_SESSION_LIFETIME"] = SESSION_LIFETIME

CORS(app, origins=CORS_ORIGINS)

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

logging.basicConfig(
    filename=LOG_FILE,
    level=getattr(logging, LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)

# ---------------------------------------------------------------------------
# Blueprints
# ---------------------------------------------------------------------------

app.register_blueprint(auth_bp)
app.register_blueprint(notes_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(files_bp)

# ---------------------------------------------------------------------------
# Database
# ---------------------------------------------------------------------------

init_db()

# ---------------------------------------------------------------------------
# Error handling
# ---------------------------------------------------------------------------

@app.errorhandler(Exception)
def handle_exception(exc):
    """Return a JSON error for any unhandled exception.  Includes the
    traceback in the response so that frontend developers can report
    meaningful bug details during development."""
    tb = traceback.format_exc()
    logging.getLogger(__name__).error("Unhandled exception:\n%s", tb)
    return jsonify({
        "error": str(exc),
        "traceback": tb,
    }), 500


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
