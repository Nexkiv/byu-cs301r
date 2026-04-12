### [Medium] Limited audit logging and lack of sensitive-data masking

**Files/areas reviewed:** `chess/server` (logging dependency), authentication and DB operations

**Findings & Explanation:**
- The codebase does not contain structured audit logging for authentication events (successful logins, failed logins, token creation, logout), administrative actions (database clear), or sensitive data access (game creation). There are `System.out` messages in client/test code and `Main` logs the server port, but no centralized audit log calls in the server business logic.
- I did not find explicit logging of tokens or passwords in server code — this is good. However, the logging backend is `slf4j-simple`, which uses a simple console logger by default; ensure production logging is configured to a secure aggregator and that no sensitive fields are logged.

**Proposed Refactor / Remediation:**
- Add structured audit logs at security-relevant events: authentication success/failure (include username, source IP, timestamp), token issuance/revocation, admin actions (who/when), and suspicious events. Do not log sensitive values such as raw tokens or passwords.
- Ensure logs are shipped securely (TLS to a log collector), have proper retention and rotation, and are protected from unauthorized access.
- Add alerting/monitoring rules for repeated failed login attempts, unexpected database clear events, and abnormal rates of token creation.

