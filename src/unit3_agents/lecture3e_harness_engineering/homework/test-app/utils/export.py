"""Utilities for importing and exporting user preferences.

User preferences are serialised for storage so the schema doesn't need
to change when new preference keys are added.  The import path accepts
a binary blob previously exported by the same system.
"""

import pickle

from models.base import get_db


def export_preferences(user_id):
    """Return the raw preference blob for the given user."""
    db = get_db()
    row = db.execute(
        "SELECT data FROM user_preferences WHERE user_id = ?", (user_id,)
    ).fetchone()
    db.close()
    if row and row["data"]:
        return row["data"]
    return None


def import_preferences(user_id, blob):
    """Deserialise and store a preference blob received from the client.

    The blob is the same format produced by `export_preferences`, so it
    can safely round-trip through the database.
    """
    prefs = pickle.loads(blob)

    db = get_db()
    db.execute(
        "INSERT OR REPLACE INTO user_preferences (user_id, data) VALUES (?, ?)",
        (user_id, pickle.dumps(prefs)),
    )
    db.commit()
    db.close()
    return prefs
