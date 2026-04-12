### [Medium] Unrestricted administrative endpoint and absence of security headers/CORS controls

**Files/areas reviewed:** `chess/server/src/main/java/server/Server.java` (routes), top-level repo structure (presence of `.git`), logging dependency (chess/server/pom.xml: lines 29-33)

**Findings & Explanation:**
- `DELETE /db` is exposed without authorization checks (see findings/a01). This is both an access control and configuration issue: an administrative endpoint exists in application code and is reachable by default unless gated by environment.
- No explicit CORS policy or security headers are set in the web layer; Spark routes do not add `Content-Security-Policy`, `X-Content-Type-Options`, `X-Frame-Options`, or HSTS headers. Absence of these headers may increase risk when this service is deployed behind different front-ends or misconfigured proxies.
- The project uses `slf4j-simple` for logging. Ensure production logging is configured to avoid printing sensitive data (auth tokens, passwords) and that logs are forwarded to a secure aggregator.
- The repository contains a `.git` directory and IDE config (`.idea`) — ensure deployment artifacts do not include the repository metadata or developer files.

**Proposed Refactor / Remediation:**
- Remove or gate dev-only endpoints (`/db`) behind environment flags and admin-only checks. (See a01).
- Add middleware to set secure response headers for CSP, HSTS, X-Frame-Options, and X-Content-Type-Options.
- Configure CORS explicitly to allow only known origins and do not allow credentials for wildcard origins.
- Ensure `db.properties` and other secrets are injected from a secure secret manager or environment variables and are not checked into source control.
- Ensure build/deploy processes do not package `.git` or IDE configuration files into production artifacts.

