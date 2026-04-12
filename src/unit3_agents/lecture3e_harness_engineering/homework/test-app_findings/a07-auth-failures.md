### [High] Passwords logged on failed login attempts

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

### [High] No brute-force protection / rate limiting on login

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

### [Medium] Session cookie options not explicitly hardened

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

