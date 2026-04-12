### [High] Sensitive flows lack server-side guards and rely on client input (notes export)

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

### [High] File upload size limit defined but not enforced before save

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

### [Medium] Traceback leaks in error responses (debug info in production)

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

