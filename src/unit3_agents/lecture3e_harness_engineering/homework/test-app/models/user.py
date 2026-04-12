from models.base import get_db


def find_user_by_username(username):
    """Look up a single user by exact username match."""
    db = get_db()
    user = db.execute(
        "SELECT * FROM users WHERE username = ?", (username,)
    ).fetchone()
    db.close()
    return user


def get_user_by_id(user_id):
    """Fetch a user record by primary key."""
    db = get_db()
    user = db.execute(
        "SELECT * FROM users WHERE id = ?", (user_id,)
    ).fetchone()
    db.close()
    return user


def create_user(username, password_hash, role="user", pw_version=2):
    """Insert a new user with a pre-hashed password."""
    db = get_db()
    db.execute(
        "INSERT INTO users (username, password, role, pw_version) VALUES (?, ?, ?, ?)",
        (username, password_hash, role, pw_version),
    )
    db.commit()
    db.close()


def update_user_role(user_id, role):
    """Promote or demote a user."""
    db = get_db()
    db.execute(
        "UPDATE users SET role = ? WHERE id = ?", (role, user_id)
    )
    db.commit()
    db.close()


def find_users_by_filter(filters):
    """Search users by dynamic filter criteria from admin dashboard.

    `filters` is a dict like {"role": "admin", "username": "jan%"}.
    Builds a safe query from known columns only.
    """
    allowed_columns = {"role", "username", "created_at"}
    db = get_db()

    clauses = []
    params = []
    for col, value in filters.items():
        if col in allowed_columns:
            clauses.append(f"{col} LIKE ?")
            params.append(value)

    where = " AND ".join(clauses) if clauses else "1=1"
    order = filters.get("order_by", "created_at")

    query = f"SELECT id, username, role, created_at FROM users WHERE {where} ORDER BY {order}"
    users = db.execute(query, params).fetchall()
    db.close()
    return users
