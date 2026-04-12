### [High] Unchecked user_id in notes export allows data exfiltration

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

### [High] File download permits arbitrary `dir` and `name` without ownership check

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

### [High] `login_required` backdoor via `_test_bypass` query param

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

