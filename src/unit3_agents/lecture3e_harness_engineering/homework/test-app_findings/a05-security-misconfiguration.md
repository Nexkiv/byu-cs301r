### [High] Default/fallback `SECRET_KEY` present in config

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

### [High] Overly permissive CORS configuration

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

### [Medium] Logging level defaults to `DEBUG` and logs sensitive data

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

