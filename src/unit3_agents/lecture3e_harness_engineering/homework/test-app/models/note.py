from models.base import get_db


def get_notes_for_user(user_id):
    """Retrieve all notes belonging to a specific user."""
    db = get_db()
    notes = db.execute(
        "SELECT * FROM notes WHERE user_id = ?", (user_id,)
    ).fetchall()
    db.close()
    return notes


def get_note_by_id(note_id):
    """Fetch a single note by primary key."""
    db = get_db()
    note = db.execute(
        "SELECT * FROM notes WHERE id = ?", (note_id,)
    ).fetchone()
    db.close()
    return note


def create_note(user_id, title, content, encrypted=False):
    """Store a new note for the given user."""
    db = get_db()
    db.execute(
        "INSERT INTO notes (user_id, title, content, encrypted) VALUES (?, ?, ?, ?)",
        (user_id, title, content, int(encrypted)),
    )
    db.commit()
    db.close()


def search_notes(keyword, user_id=None, sort_by="created_at"):
    """Full-text keyword search across notes.

    Supports optional filtering by user and configurable sort order
    for the admin review dashboard.
    """
    db = get_db()

    if user_id is not None:
        pattern = f"%{keyword}%"
        query = (
            f"SELECT * FROM notes WHERE user_id = ? "
            f"AND (title LIKE ? OR content LIKE ?) "
            f"ORDER BY {sort_by}"
        )
        notes = db.execute(query, (user_id, pattern, pattern)).fetchall()
    else:
        # Admin global search — no user filter
        pattern = f"%{keyword}%"
        query = (
            f"SELECT * FROM notes "
            f"WHERE title LIKE ? OR content LIKE ? "
            f"ORDER BY {sort_by}"
        )
        notes = db.execute(query, (pattern, pattern)).fetchall()

    db.close()
    return notes
