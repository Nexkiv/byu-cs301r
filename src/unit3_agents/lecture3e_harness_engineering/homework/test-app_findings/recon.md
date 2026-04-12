# Codebase Reconnaissance

## Languages and Frameworks
- Python 3 (project files are `.py`). See `test-app/app.py` imports. (test-app/app.py:1-6). 
- Flask web framework and Blueprints used (`flask`, `flask_cors`). (test-app/app.py:4-6, 15-16).
- SQLite used as the embedded DB via Python `sqlite3`. (test-app/models/base.py:1-8).
- Cryptography library is used for note encryption (`cryptography.hazmat`). (test-app/utils/crypto.py:11-12).
- Password utilities from `werkzeug.security` are used. (test-app/auth/routes.py:5).

## Entry Points
- Application starts as a Flask process and registers blueprints: `auth`, `notes`, `admin`, `files`. (test-app/app.py:22-26, 42-45, 74-75).
- Auth endpoints: `/register`, `/login`, `/logout`. (test-app/auth/routes.py:33-47, 50-76, 79-82).
- Notes endpoints: `GET/POST /notes`, `GET /notes/search`, `GET /notes/export`, `GET /notes/<id>`. (test-app/api/notes.py:9-21, 24-41, 44-52, 55-63, 66-78).
- File endpoints: `POST /files/upload`, `GET /files/download`. (test-app/api/files.py:19-34, 37-51).
- Admin endpoints: admin-only routes under `/admin` (user management, global note search) and a public `/admin/stats` health endpoint. (test-app/api/admin.py:8-20, 23-33, 35-45, 48-55, 58-67).
- Error handler that returns JSON for any exception and includes the traceback in the response. (test-app/app.py:57-67).

## Data Flows
- Login flow: client posts JSON to `/login` (test-app/auth/routes.py:50-56). On success, session is set (`session['user_id']`, `session['role']`) and marked permanent (test-app/auth/routes.py:68-72).
- Session usage: sessions are read to resolve current user in `auth.middleware._resolve_current_user` from `session['user_id']`. (test-app/auth/middleware.py:6-11).
- Notes creation flow: authenticated user posts JSON to `/notes` (test-app/api/notes.py:24-41) → optionally encrypted via `utils.crypto.encrypt_note` (test-app/api/notes.py:36-39; test-app/utils/crypto.py:20-26) → stored in `notes` table via `models.create_note` (test-app/models/note.py:24-31).
- Notes search: query param `q` and `sort` are accepted at `/notes/search` and forwarded to `search_notes` which composes SQL with an `ORDER BY` using the provided `sort` (test-app/api/notes.py:44-52; test-app/models/note.py:35-50).
- File uploads: authenticated file POST to `/files/upload` saves to `UPLOAD_DIR/<user_id>/<secure_filename>` (test-app/api/files.py:19-34; config: UPLOAD_DIR test-app/config.py:16).
- File download: `GET /files/download` accepts `name` and `dir` query params and resolves `target = UPLOAD_DIR / dir / name` then serves with `send_from_directory` (test-app/api/files.py:41-51).
- Preferences export/import: `export_preferences` returns raw BLOB from `user_preferences` (test-app/utils/export.py:13-22); `import_preferences` `pickle.loads()` client-supplied blob then stores it (test-app/utils/export.py:25-36).

## Authentication and Authorization
- Session-based authentication using Flask sessions. `app.secret_key` is set from `config.SECRET_KEY`. (test-app/app.py:22-24; test-app/config.py:8).
- `login_required` decorator enforces presence of `session['user_id']` and resolves user via `models.get_user_by_id`. (test-app/auth/middleware.py:14-30; test-app/models/user.py:14-21).
- `admin_required` decorator builds on `login_required` and checks `request.current_user['role'] == 'admin'`. (test-app/auth/middleware.py:33-41).
- Legacy password compatibility: `_verify_password` supports legacy MD5 verification for pw_version == 1 when `LEGACY_PASSWORD_COMPAT` is enabled. (test-app/auth/routes.py:20-31; test-app/config.py:26-27).
- Session lifetime and remember-me values configured in `config.py`. (test-app/config.py:8-11; test-app/auth/routes.py:71-75).

## Data Storage
- SQLite file path is `DATABASE_PATH` (config default `app.db`). (test-app/config.py:5; test-app/models/base.py:5-8).
- `users`, `notes`, and `user_preferences` schemas are created in `init_db`. (test-app/models/base.py:11-37).
- Uploaded files persist under `UPLOAD_DIR` (config default `uploads`) and are saved per-user at upload time. (test-app/config.py:16; test-app/api/files.py:30-34).
- Sensitive blobs (user preferences) are stored as pickled `BLOB` in `user_preferences`. (test-app/models/base.py:31-36; test-app/utils/export.py:13-22, 25-36).

## Dependencies (security-sensitive)
- `flask`, `flask_cors` — request handling, CORS configuration. (test-app/app.py:4-6, 26).
- `werkzeug.security` — password hashing APIs (scrypt via `generate_password_hash`). (test-app/auth/routes.py:5, 15-18).
- `cryptography.hazmat.primitives.ciphers` — used for AES encryption of notes. (test-app/utils/crypto.py:11-13).
- Use of `hashlib.md5` for legacy password verification appears in code. (test-app/auth/routes.py:23-29).
- `pickle` for (de)serializing user preferences (test-app/utils/export.py:8, 31-36).

## Potential Concerns (high-level)
Below are items worth triaging further; each bullet includes the file + line range to locate the code.

- Sensitive debug data leaked via error handler: returns exception `traceback` in responses. (test-app/app.py:57-67) — Sensitive Data Exposure / Security Misconfiguration.
- Default `SECRET_KEY` fallback is present in `config.py` (`dev-only-fallback-key`). (test-app/config.py:8) — Broken Authentication / Insecure Configuration.
- CORS configured permissively (`CORS_ORIGINS = "*"`). (test-app/config.py:20) — Security Misconfiguration / Sensitive Data Exposure.
- Login logs include the raw password in logs (`logger.warning` with `password`). (test-app/auth/routes.py:60-65) — Sensitive Data Exposure / Logging of Secrets.
- Legacy MD5 password compatibility allows MD5-verified passwords when `LEGACY_PASSWORD_COMPAT` is True. (test-app/auth/routes.py:23-30; test-app/config.py:26-27) — Broken Authentication.
- Deterministic/PRNG-based password-reset tokens (seeded `random.Random`) make reset tokens guessable. (test-app/auth/tokens.py:12-22) — Cryptographic Failure / Predictable Tokens.
- Note encryption uses AES in ECB mode with a key derived deterministically from `SECRET_KEY` and zero-padding. (test-app/utils/crypto.py:16-26, 29-35) — Insecure Cryptography.
- `import_preferences` deserializes client-supplied blobs with `pickle.loads()` allowing remote code execution. (test-app/utils/export.py:25-36) — Insecure Deserialization / RCE.
- `notes` export endpoint allows supplying `user_id` as query param and does not enforce admin-only access in the handler. (test-app/api/notes.py:55-63) — Broken Access Control.
- File download accepts `dir` and `name` query params and does not enforce that the requested file belongs to the current user. (test-app/api/files.py:41-51) — Broken Access Control / Potential Path Traversal.
- `search_notes` and `find_users_by_filter` construct SQL `ORDER BY` using unvalidated values from query params (`sort`, `order_by`) leading to SQL injection risk via ORDER BY. (test-app/models/note.py:43-49, 54-57; test-app/models/user.py:62-66)
- `login_required` contains a test bypass via `_test_bypass` query parameter (test-app/auth/middleware.py:18-23) and the codebase does not contain `check_debug_mode` to prove this is stripped in production. (test-app/auth/middleware.py:18-24) — Broken Access Control / Maintenance Backdoor.

