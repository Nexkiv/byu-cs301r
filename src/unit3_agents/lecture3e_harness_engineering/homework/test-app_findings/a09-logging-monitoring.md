### [High] Sensitive secrets (passwords) written to logs

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

### [Medium] Tracebacks logged and returned in responses

**File:** `test-app/app.py:57-67`

**Vulnerable Code:**
```
logging.getLogger(__name__).error("Unhandled exception:\n%s", tb)
return jsonify({"error": str(exc), "traceback": tb}), 500
```

**Explanation:** Tracebacks are both logged and returned in API responses. While logging tracebacks is useful, returning them to clients leaks internal state. It's also unclear whether log rotation, retention, and access controls are configured for the log file defined by `LOG_FILE`.

**Proposed Refactor:** Log full tracebacks server-side, but return a generic error to clients. Ensure log rotation and secure file permissions are configured (e.g., use `logging.handlers.RotatingFileHandler` and restrict file access to the application user).

