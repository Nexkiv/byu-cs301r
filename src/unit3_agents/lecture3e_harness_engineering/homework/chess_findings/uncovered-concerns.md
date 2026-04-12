# Uncovered Concerns

Recon entries not referenced by any auditor in this run.

- `WebSocketHandler.java: lines 36-41, 61-69` — Suspected category: [auth-failures]
- `- No rate limiting, no CSRF protection for the HTTP endpoints exposed (server module has no middleware shown for rate limiting or CSRF). (Server.java: overall routing lines 35-50).` — Suspected category: [insecure-design]
- `CREATE TABLE` — Suspected category: [other]
