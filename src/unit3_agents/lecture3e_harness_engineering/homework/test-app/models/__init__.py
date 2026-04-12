from models.base import get_db, init_db
from models.user import (
    find_user_by_username,
    get_user_by_id,
    create_user,
    find_users_by_filter,
    update_user_role,
)
from models.note import (
    get_notes_for_user,
    create_note,
    search_notes,
    get_note_by_id,
)
