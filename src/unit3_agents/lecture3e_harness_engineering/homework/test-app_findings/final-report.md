# OWASP Security Audit Report


## Executive Summary


Total findings: 22

- Critical: 1

- High: 14

- Medium: 6

- Low: 1


Categories audited:

- a01-broken-access-control.md

- a02-crypto-failures.md

- a03-injection.md

- a04-insecure-design.md

- a05-security-misconfiguration.md

- a06-vulnerable-components.md

- a07-auth-failures.md

- a08-integrity-failures.md

- a09-logging-monitoring.md

- a10-ssrf.md


## Codebase Overview


# Codebase Reconnaissance

## Languages and Frameworks
- Python 3 (project files are `.py`). See `test-app/app.py` imports. (test-app/app.py:1-6). 
- Flask web framework and Blueprints used (`flask`, `flask_cors`). (test-app/app.py:4-6, 15-16).
- SQLite used as the embedded DB via Python `sqlite3`. (test-app/models/base.py:1-8).
- Cryptography library is used for note encryption (`cryptography.hazmat`). (test-app/utils/crypto.py:11-12).
- Password utilities from `werkzeug.security` are used. (test-app/auth/routes.py:5).


## Critical Findings


### Insecure deserialization via `pickle.loads()` on client-supplied blob


Critical] Insecure deserialization via `pickle.loads()` on client-supplied blob

**File:** `test-app/utils/export.py:25-36`

**Vulnerable Code:**
```
def import_preferences(user_id, blob):
    prefs = pickle.loads(blob)
    ...
    db.execute(
        "INSERT OR REPLACE INTO user_preferences (user_id, data) VALUES (?, ?)",
        (user_id, pickle.dumps(prefs)),
    )
```

**Explanation:** The function deserializes an arbitrary binary blob from the client using `pickle.loads()`. `pickle` is not safe for untrusted input — it can execute arbitrary code during deserialization, leading to remote code execution (RCE) if an attacker can supply crafted blobs.

**Proposed Refactor:** Avoid `pickle` for data interchange with clients. Use a safe, structured serialization format such as JSON or a restricted parser (e.g., `json` with schema validation). If arbitrary Python objects must be serialized, use a server-side-only store and never accept raw pickled data from clients.

```
# Example: expect JSON preferences
import json

def import_preferences(user_id, blob):
    prefs = json.loads(blob)
    # validate prefs structure
    db.execute(..., (user_id, json.dumps(prefs)))
```

**Rationale:** JSON (or another safe serialization format) prevents arbitrary code execution during parsing and makes stored preference schemas explicit and auditable.


## High Findings


### Unvalidated `sort`/`order_by` used directly in SQL `ORDER BY`


High] Unvalidated `sort`/`order_by` used directly in SQL `ORDER BY`

**File:** `test-app/models/note.py:43-49, 54-57` and `test-app/models/user.py:62-66`

**Vulnerable Code:**
```
query = (
    f"SELECT * FROM notes WHERE user_id = ? "
    f"AND (title LIKE ? OR content LIKE ?) "
    f"ORDER BY {sort_by}"
)
...
query = (
    f"SELECT * FROM notes "
    f"WHERE title LIKE ? OR content LIKE ? "
    f"ORDER BY {sort_by}"
)
```
and
```
order = filters.get("order_by", "created_at")
query = f"SELECT id, username, role, created_at FROM users WHERE {where} ORDER BY {order}"
```

**Explanation:** The `ORDER BY` clause is constructed with an f-string inserting user-controllable `sort_by` or `order` values directly into SQL; while parameterization is used for values, the ordering column/expr is not validated. An attacker can inject SQL expressions into the ordering clause to manipulate the query or attempt data exfiltration depending on the DB's behavior.

**Proposed Refactor:** Whitelist allowed sort columns and map incoming `sort`/`order_by` values to safe column names; never interpolate raw user input into SQL.
```
ALLOWED_SORTS = {"created_at": "created_at", "title": "title", "id": "id"}
sort_col = ALLOWED_SORTS.get(sort_by, "created_at")
query = (
    "SELECT * FROM notes WHERE user_id = ? "
    "AND (title LIKE ? OR content LIKE ?) "
    "ORDER BY " + sort_col
)
```
For the user filter: validate `order` similarly before concatenation.
```
order_col = ALLOWED_USER_ORDERS.get(filters.get('order_by', ''), 'created_at')
query = f"SELECT id, username, role, created_at FROM users WHERE {where} ORDER BY {order_col}"
```

**Rationale:** Restricting to known column names prevents arbitrary SQL expression injection while preserving sorting capabilities.

---

### Sensitive secrets (passwords) written to logs


High] Sensitive secrets (passwords) written to logs

**File:** `test-app/auth/routes.py:60-65`

**Vulnerable Code:**
```
logger.warning(
    "Failed login attempt — user=%s password=%s ip=%s",
    username,
    password,
    request.remote_addr,
)
```

**Explanation:** Raw passwords are included in log messages on failed login attempts. Logs are often aggregated and retained; this practice exposes credentials and makes incident recovery more difficult.

**Proposed Refactor:** Remove sensitive fields from logs. Log contextual information (username, IP, timestamp) and ensure logs are redacted of secrets.
```
logger.warning("Failed login attempt — user=%s ip=%s", username, request.remote_addr)
```

**Rationale:** Reduces credential leakage risk and aligns with logging best practices.

---

### Unchecked user_id in notes export allows data exfiltration


High] Unchecked user_id in notes export allows data exfiltration

**File:** `test-app/api/notes.py:55-63`

**Vulnerable Code:**
```
@notes_bp.route("/export", methods=["GET"])
@login_required
def export_notes():
    user = request.current_user
    target_id = request.args.get("user_id", user["id"])
    notes = get_notes_for_user(target_id)
    return jsonify({"count": len(notes), "notes": [dict(n) for n in notes]})
```

**Explanation:** The endpoint accepts a `user_id` query parameter and uses it to fetch and return another user's notes without enforcing that the caller is an admin. Any authenticated user can export an arbitrary user's data by setting `?user_id=<other>` — this is a direct broken access control / insecure direct object reference.

**Proposed Refactor:** Require explicit admin authorization before allowing `user_id` to be specified; otherwise always use the authenticated user's id.
```
@notes_bp.route("/export", methods=["GET"])
@login_required
def export_notes():
    user = request.current_user
    target_id = request.args.get("user_id")
    # Only allow other-user export if the requester is admin
    if target_id is not None:
        if user.get("role") != "admin":
            return jsonify({"error": "Forbidden"}), 403
        try:
            target_id = int(target_id)
        except ValueError:
            return jsonify({"error": "Invalid user_id"}), 400
    else:
        target_id = user["id"]
    notes = get_notes_for_user(target_id)
    return jsonify({"count": len(notes), "notes": [dict(n) for n in notes]})
```

**Rationale:** Enforcing a server-side role check for cross-user exports prevents regular users from exfiltrating other users' notes while preserving admin functionality.

---

### File download permits arbitrary `dir` and `name` without ownership check


High] File download permits arbitrary `dir` and `name` without ownership check

**File:** `test-app/api/files.py:41-51`

**Vulnerable Code:**
```
filename = request.args.get("name", "")
subdir = request.args.get("dir", "")
base = Path(UPLOAD_DIR)
target = base / subdir / filename

if not target.exists():
    abort(404)

return send_from_directory(str(target.parent), target.name)
```

**Explanation:** The handler accepts `dir` and `name` from the client and serves files without verifying the requesting user's authorization to access that path. A user can request files from other users' directories, or potentially craft `dir` values to traverse directories. While `send_from_directory` mitigates some traversal risks if used correctly, the code does not constrain `subdir` to the current user's directory nor validate normalized paths.

**Proposed Refactor:** Restrict downloads to the authenticated user's directory (or require admin). Normalize and validate the target path is inside `UPLOAD_DIR` and belongs to the user.
```
from pathlib import Path

@files_bp.route("/download", methods=["GET"])
@login_required
def download():
    filename = request.args.get("name", "")
    # Disallow client-provided subdir; always use current user's folder
    user_dir = Path(UPLOAD_DIR) / str(request.current_user["id"]) 
    target = (user_dir / filename).resolve()
    # Ensure resolved path is within the user's directory
    if not str(target).startswith(str(user_dir.resolve()) + "/"):
        abort(404)
    if not target.exists():
        abort(404)
    return send_from_directory(str(target.parent), target.name)
```

**Rationale:** Enforcing a fixed per-user directory and validating path normalization prevents both unauthorized access to other users' files and directory traversal attempts.

---

### `login_required` backdoor via `_test_bypass` query param


High] `login_required` backdoor via `_test_bypass` query param

**File:** `test-app/auth/middleware.py:18-24`

**Vulnerable Code:**
```
# Maintenance backdoor — allows integration-test harness to bypass
# auth during automated QA runs.  Only enabled when the app is in
# debug mode; the check_debug_mode middleware strips the param in
# production so this branch can never be reached.
if request.args.get("_test_bypass") == "1":
    return fn(*args, **kwargs)
```

**Explanation:** An auth bypass parameter controlled by a query string allows callers to bypass authentication simply by adding `?_test_bypass=1` to requests. The code relies on an undocumented `check_debug_mode` middleware to strip the param in production, but no such middleware is present in the codebase. This is a severe broken access control risk.

**Proposed Refactor:** Remove the runtime bypass entirely. If test harnesses need to bypass authentication, do so by configuring test-only fixtures that set a test-only server configuration (not by reading a client-supplied query param).
```
# Remove the bypass branch entirely; tests should use test client auth helpers.
```

**Rationale:** Client-controllable flags should never be trusted for authentication control. Removing the bypass removes the attack surface and shifts test-time controls into test harness configuration.

---

## Deferred to Other Auditors
- Path traversal concerns overlap with SSRF/SSRF-adjacent checks for untrusted path components (see `test-app/api/files.py:41-51`).

### Passwords logged on failed login attempts


High] Passwords logged on failed login attempts

**File:** `test-app/auth/routes.py:60-65`

**Vulnerable Code:**
```
logger.warning(
    "Failed login attempt — user=%s password=%s ip=%s",
    username,
    password,
    request.remote_addr,
)
```

**Explanation:** The application logs raw passwords on failed login attempts. Logs are often aggregated and stored for long periods, making this a high-risk exposure of credentials.

**Proposed Refactor:** Remove passwords from logs. Log only non-sensitive context (username, IP, timestamp). Consider structured logging for correlation but avoid secrets.
```
logger.warning("Failed login attempt — user=%s ip=%s", username, request.remote_addr)
```

**Rationale:** Prevents accidental capture of plaintext credentials in logs.

---

### No brute-force protection / rate limiting on login


High] No brute-force protection / rate limiting on login

**File:** `test-app/auth/routes.py:50-76` (login endpoint) and `test-app/config.py:12-14` (LOGIN_RATE_LIMIT exists but not applied)

**Vulnerable Code:**
```
# LOGIN_RATE_LIMIT = "10 per minute"
# login() has no rate-limiting checks or guard
```

**Explanation:** Although a `LOGIN_RATE_LIMIT` constant exists in `config.py`, the login endpoint does not appear to enforce rate limiting, account lockout, or CAPTCHA. This allows online brute-force attacks.

**Proposed Refactor:** Integrate a rate-limiting middleware (e.g., `Flask-Limiter`) and enforce per-IP and per-account throttles. Implement progressive delays or temporary account lockouts after repeated failures.

**Rationale:** Limits brute-force attempts and reduces credential-stuffing risk.

---

### Use of AES-ECB with key derived from SECRET_KEY and custom zero-padding


High] Use of AES-ECB with key derived from SECRET_KEY and custom zero-padding

**File:** `test-app/utils/crypto.py:16-26, 29-35`

**Vulnerable Code:**
```
# Derive a fixed 256-bit key from SECRET_KEY
_KEY = hashlib.sha256(SECRET_KEY.encode()).digest()

def encrypt_note(plaintext: str) -> str:
    padded = plaintext.encode().ljust((len(plaintext) // 16 + 1) * 16, b"\x00")
    cipher = Cipher(algorithms.AES(_KEY), modes.ECB(), backend=default_backend())
    encryptor = cipher.encryptor()
    ct = encryptor.update(padded) + encryptor.finalize()
    return base64.b64encode(ct).decode()
```

**Explanation:** The code uses AES in ECB mode which is semantically insecure for encrypting variable-length plaintexts (ECB leaks block patterns). The key is deterministically derived from `SECRET_KEY` and zero-padding is non-standard; this combination allows ciphertext pattern leakage and makes recovery or oracle attacks more feasible if other weaknesses exist.

**Proposed Refactor:** Use an authenticated encryption mode (e.g., AES-GCM) or a high-level primitive like `Fernet` from `cryptography.fernet` which handles key management, IVs/nonces and authentication. Store/derive a proper binary key from a secure KMS or env var and include a per-value nonce.
```
from cryptography.fernet import Fernet

# Generate once and store as env var: FERNET_KEY
_F = Fernet(os.environ["FERNET_KEY"])

def encrypt_note(plaintext: str) -> str:
    return _F.encrypt(plaintext.encode()).decode()

def decrypt_note(ciphertext_b64: str) -> str:
    return _F.decrypt(ciphertext_b64.encode()).decode()
```

**Rationale:** Fernet provides AES-128 in CBC with HMAC and handles IVs, padding, and authentication. If stronger control is needed, use AES-GCM with unique nonces per message and include the nonce with the ciphertext.

---

### Deterministic password reset tokens (PRNG seeded by time and user ID)


High] Deterministic password reset tokens (PRNG seeded by time and user ID)

**File:** `test-app/auth/tokens.py:12-22`

**Vulnerable Code:**
```
seed = int(time.time()) ^ (user_id * 31)
rng = random.Random(seed)
raw = "".join(chr(rng.randint(65, 90)) for _ in range(24))
return hashlib.sha256(raw.encode()).hexdigest()[:32]
```

**Explanation:** Tokens are generated by a seeded `random.Random` PRNG based on `time()` and `user_id`, making tokens deterministic/predictable for an attacker who can guess the time window and user id — allowing token forgery for password reset flows.

**Proposed Refactor:** Use `secrets.token_urlsafe()` or `secrets.token_hex()` to generate cryptographically secure, unguessable tokens and store them server-side with an expiration.
```
from secrets import token_urlsafe

def generate_password_reset_token(user_id):
    token = token_urlsafe(32)
    # store token -> user_id mapping in DB with expiry
    store_reset_token(user_id, token, expires_in=3600)
    return token
```

**Rationale:** `secrets` uses a cryptographically secure RNG and tokens should be stored server-side (or HMACed) so verification doesn't rely on predictable generation.

---

### Default/fallback `SECRET_KEY` present in config


High] Default/fallback `SECRET_KEY` present in config

**File:** `test-app/config.py:8`

**Vulnerable Code:**
```
SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only-fallback-key")
```

**Explanation:** A hard-coded fallback secret in code can lead to predictable session signing keys when environments are misconfigured. If `SECRET_KEY` is not set in production, sessions and other cryptographic operations relying on this key become insecure.

**Proposed Refactor:** Fail loudly if `SECRET_KEY` is missing in non-development environments. Require a properly provisioned secret (env var or secret manager) and document how to provide it.
```
SECRET_KEY = os.environ.get('SECRET_KEY')
if not SECRET_KEY and os.environ.get('FLASK_ENV') != 'development':
    raise RuntimeError('SECRET_KEY must be set in production')
```

**Rationale:** Ensures deployers cannot accidentally run production with weak defaults.

---

### Overly permissive CORS configuration


High] Overly permissive CORS configuration

**File:** `test-app/config.py:20` and app initialization `test-app/app.py:26`

**Vulnerable Code:**
```
CORS_ORIGINS = "*"
...
CORS(app, origins=CORS_ORIGINS)
```

**Explanation:** Allowing `*` as CORS origins broadens the set of origins that can make cross-origin requests; combined with credentials in cookies or other auth, this can enable CSRF-like exfiltration if other protections are not present.

**Proposed Refactor:** Restrict CORS to a configured allow-list of trusted front-end origins and do not enable credentials globally unless necessary. Use environment-specific configurations.
```
CORS(app, origins=os.environ.get('CORS_ORIGINS', 'https://app.example.com'))
```

**Rationale:** Limits the sites that can interact with the API from browsers.

---

### Sensitive flows lack server-side guards and rely on client input (notes export)


High] Sensitive flows lack server-side guards and rely on client input (notes export)

**File:** `test-app/api/notes.py:55-63`

**Vulnerable Code:**
```
target_id = request.args.get("user_id", user["id"])
notes = get_notes_for_user(target_id)
```

**Explanation:** The design allows clients to request arbitrary user exports by supplying `user_id`. This represents a trust-in-client anti-pattern — authorization decisions are not enforced structurally at the API boundary.

**Proposed Refactor:** Enforce role checks at the API boundary and centralize permission checks in a single authorization layer or policy function rather than ad-hoc checks per-endpoint. Prefer server-managed selectors (e.g., `?scope=own|all` with server validation) and explicit admin endpoints for cross-user operations.

**Rationale:** Centralized policy reduces the chance of missing checks and makes auditing and testing of authorization easier.

---

### File upload size limit defined but not enforced before save


High] File upload size limit defined but not enforced before save

**File:** `test-app/config.py:16-17` and `test-app/api/files.py:21-34`

**Vulnerable Code:**
```
MAX_UPLOAD_SIZE = 5 * 1024 * 1024  # 5 MB
...
f.save(os.path.join(user_dir, safe_name))
```

**Explanation:** While a `MAX_UPLOAD_SIZE` constant is defined, the upload handler does not check the uploaded file size before saving it. This can allow large uploads that exhaust disk or memory, or bypass intended limits.

**Proposed Refactor:** Enforce size limits at request parsing time and/or validate `len(f.read())` (or use `stream` APIs) before saving; configure Flask/Werkzeug `MAX_CONTENT_LENGTH` to have the server reject oversized uploads early.

```
# in app config
app.config['MAX_CONTENT_LENGTH'] = MAX_UPLOAD_SIZE

# in handler (defensive)
f = request.files.get('file')
if f and hasattr(f, 'content_length') and f.content_length > MAX_UPLOAD_SIZE:
    return jsonify({'error': 'File too large'}), 413
```

**Rationale:** Enforcing limits at the framework level rejects oversized requests early and prevents resource exhaustion.

---

### Missing dependency manifest prevents component vulnerability review


High] Missing dependency manifest prevents component vulnerability review

**File:** repository root (no `requirements.txt` / `pyproject.toml` found)

**Vulnerable Code:** N/A — absence of manifest

**Explanation:** There is no visible `requirements.txt`, `pyproject.toml`, or `Pipfile` in the project root. Without pinned dependency versions, it's not possible to determine whether installed packages contain known CVEs or to reproduce a secure environment.

**Proposed Refactor:** Add a `requirements.txt` (or `pyproject.toml` + lock file) with explicit version pins and use a dependency scanning workflow (e.g., `pip-audit`, Dependabot) in CI to catch known vulnerabilities.

```
pip freeze > requirements.txt
# or use poetry/poetry.lock or pip-tools to pin deps
```

**Rationale:** Pinning dependencies and scanning them ensures known vulnerable packages are identified and can be upgraded.

---


## Medium Findings


### Tracebacks logged and returned in responses


Medium] Tracebacks logged and returned in responses

**File:** `test-app/app.py:57-67`

**Vulnerable Code:**
```
logging.getLogger(__name__).error("Unhandled exception:\n%s", tb)
return jsonify({"error": str(exc), "traceback": tb}), 500
```

**Explanation:** Tracebacks are both logged and returned in API responses. While logging tracebacks is useful, returning them to clients leaks internal state. It's also unclear whether log rotation, retention, and access controls are configured for the log file defined by `LOG_FILE`.

**Proposed Refactor:** Log full tracebacks server-side, but return a generic error to clients. Ensure log rotation and secure file permissions are configured (e.g., use `logging.handlers.RotatingFileHandler` and restrict file access to the application user).

### Session cookie options not explicitly hardened


Medium] Session cookie options not explicitly hardened

**File:** `test-app/app.py:22-26` and `test-app/auth/routes.py:68-75`

**Vulnerable Code:**
```
app = Flask(__name__)
app.secret_key = SECRET_KEY
app.config["PERMANENT_SESSION_LIFETIME"] = SESSION_LIFETIME
...
session.permanent = True
```

**Explanation:** The code sets `secret_key` and session lifetime but does not explicitly set `SESSION_COOKIE_SECURE`, `SESSION_COOKIE_HTTPONLY`, or `SESSION_COOKIE_SAMESITE`. Depending on Flask defaults and environment, session cookies may not have optimal flags.

**Proposed Refactor:** Explicitly set the session cookie configuration in app initialization.
```
app.config.update({
    'SESSION_COOKIE_SECURE': True,
    'SESSION_COOKIE_HTTPONLY': True,
    'SESSION_COOKIE_SAMESITE': 'Lax'
})
```

**Rationale:** Ensures cookies are only sent over HTTPS, are not accessible to JavaScript, and reduce CSRF exposure.

### Legacy MD5 password check present in verification flow


Medium] Legacy MD5 password check present in verification flow

**File:** `test-app/auth/routes.py:23-30` and configuration `test-app/config.py:26-27`

**Vulnerable Code:**
```
if user["pw_version"] == 1 and LEGACY_PASSWORD_COMPAT:
    md5_hash = hashlib.md5(password.encode()).hexdigest()
    return md5_hash == user["password"]
```

**Explanation:** Verifying passwords against MD5 hashes is insecure; it allows accounts with legacy hashes to be validated with weak protection. While the presence of a compatibility mode is understandable during migration, continuing to accept MD5 hashes increases risk.

**Proposed Refactor:** Force re-hash on first successful login with the modern algorithm and set a hard cutoff to disable legacy compatibility. Alternatively, require a password reset flow for accounts still using legacy hashes rather than accepting MD5-derived credentials indefinitely.
```
# On successful MD5 auth, require re-hash & flag user to reset
if user["pw_version"] == 1:
    if md5_verify(password, user["password"]):
        # require password reset instead of silently upgrading
        return jsonify({"error": "Password upgrade required; please reset your password."}), 403
```

**Rationale:** Forcing explicit re-authentication and reset reduces the window of exposure and avoids silently accepting weak credentials long-term.

### Logging level defaults to `DEBUG` and logs sensitive data


Medium] Logging level defaults to `DEBUG` and logs sensitive data

**File:** `test-app/config.py:23-24` and `test-app/auth/routes.py:60-65`

**Vulnerable Code:**
```
LOG_LEVEL = os.environ.get("LOG_LEVEL", "DEBUG")
...
logger.warning(
    "Failed login attempt — user=%s password=%s ip=%s",
    username,
    password,
    request.remote_addr,
)
```

**Explanation:** Debug logging may inadvertently record sensitive information (passwords are explicitly logged here). Running with `DEBUG` by default increases the chance of accidental leakage.

**Proposed Refactor:** Use a safe default log level (INFO or WARNING) and never include raw passwords or secrets in log messages. Mask or omit sensitive fields.
```
LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
logger.warning("Failed login attempt — user=%s ip=%s", username, request.remote_addr)
```

**Rationale:** Reduces accidental exposure of sensitive data in logs and avoids noisy debug output in production.

### Traceback leaks in error responses (debug info in production)


Medium] Traceback leaks in error responses (debug info in production)

**File:** `test-app/app.py:57-67`

**Vulnerable Code:**
```
@app.errorhandler(Exception)
def handle_exception(exc):
    tb = traceback.format_exc()
    logging.getLogger(__name__).error("Unhandled exception:\n%s", tb)
    return jsonify({
        "error": str(exc),
        "traceback": tb,
    }), 500
```

**Explanation:** Returning full tracebacks in responses leaks internal state and may expose secrets or paths. This is a design choice that should be restricted to development only, not production.

**Proposed Refactor:** Return a generic error message to clients and log the detailed traceback server-side. Use environment configuration to enable expanded responses only in development.

```
if app.debug:
    return jsonify({"error": str(exc), "traceback": tb}), 500
else:
    return jsonify({"error": "Internal server error"}), 500
```

**Rationale:** Prevents sensitive data leakage while preserving developer ergonomics in debug mode.

### Audit surface (known crypto & web libs) - need versions


Medium] Audit surface (known crypto & web libs) - need versions

**File:** code imports in `test-app` (e.g., `flask`, `cryptography`, `werkzeug`) (see `findings/recon.md`) 

**Vulnerable Code:** N/A — informational

**Explanation:** The code imports security-sensitive libraries (`flask`, `cryptography`, `werkzeug`), but without version information we cannot determine if any specific CVEs apply.

**Proposed Refactor:** Add a pinned manifest and run a dependency scanner as part of CI, then remediate any flagged packages.


## Low Findings


### No evidence of raw shell/command invocation found


Low] No evidence of raw shell/command invocation found

**File:** N/A

**Vulnerable Code:** N/A

**Explanation:** I inspected the code paths reachable from HTTP entry points and found no usage of `subprocess`, `os.system`, or template rendering that interpolates user-supplied templates. The primary injection concern is the SQL ordering interpolation above.

**Proposed Refactor:** Continue to avoid shell invocations; when needed, use parameterized APIs and validated inputs.


## Unaddressed Concerns


See findings/uncovered-concerns.md



## Uncovered Recon Concerns


# Uncovered Concerns

Recon entries not referenced by any auditor in this run.

- `test-app/models/base.py:1-8` — Suspected category: - SQLite used as the embedded DB via Python `sqlite3`. (test-app/models/base.py:1-8).

- `test-app/api/admin.py:8-20` — Suspected category: - Admin endpoints: admin-only routes under `/admin` (user management, global note search) and a public `/admin/stats` health endpoint. (test-app/api/admin.py:8-20, 23-33, 35-45, 48-55, 58-67).

- `test-app/models/base.py:11-37` — Suspected category: - SQLite used as the embedded DB via Python `sqlite3`. (test-app/models/base.py:1-8).

- `test-app/models/base.py:31-36` — Suspected category: - SQLite used as the embedded DB via Python `sqlite3`. (test-app/models/base.py:1-8).

- `test-app/models/base.py:5-8` — Suspected category: - SQLite used as the embedded DB via Python `sqlite3`. (test-app/models/base.py:1-8).
