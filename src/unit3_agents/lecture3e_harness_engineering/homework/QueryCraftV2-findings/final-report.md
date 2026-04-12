Final Security Audit Report


---

## recon.md

Codebase Reconnaissance

Languages and Frameworks
- TypeScript/JavaScript monorepo. Files: QueryCraftV2/package.json and packages/server/package.json

Entry Points
- packages/server/src/index.ts lines 8-12: server start
- packages/server/src/app.ts lines 42-50: route mounts
- /api/query/execute: packages/server/src/routes/query.routes.ts lines 40-58

Auth
- JWT in cookie qc_session; see middleware at packages/server/src/middleware/auth.middleware.ts lines 6-14

Data flows
- Route -> executeQuery -> adapters

Dependencies
- See packages/server/package.json lines 12-27

Potential concerns
- JWT secret handling, SQL adapter usage, dependency vulnerabilities, secret leakage

---

## a01-broken-access-control.md

[Medium] Missing explicit role checks on admin routes

File: packages/server/src/app.ts:48

Finding: admin routes are mounted at /api/admin but review should verify role enforcement in handlers and role.middleware usage.

Proposed Fix: Ensure role.middleware enforces admin role at route level and in service entry points.
---

## a02-crypto-failures.md

[Low] JWT secret and bcrypt present

File: packages/server/src/routes/auth.routes.ts:38-47

Finding: JWT is signed using env.JWT_SECRET; confirm secret management and rotation. bcrypt used for passwords, which is appropriate.

Proposed Fix: Use strong managed secret (vault) and rotate tokens periodically.
---

## a03-injection.md

[High] SQL injection risks if raw SQL bypasses sqlGuard

File: packages/server/src/services/queryExecutor.ts and packages/server/src/adapters/*.ts
Finding: SQL is parsed and filtered in sqlGuard, but any code paths that pass user input directly to adapters or use string concatenation should be reviewed.

Proposed Fix: Require parameterized queries at adapter layer and centralize sanitization.
---

## a04-insecure-design.md

[Medium] Broad privileges for query execution

File: packages/server/src/routes/query.routes.ts:40-58

Finding: Student/admin modes differ; ensure role separation and least privilege for execution contexts.

Proposed Fix: Separate execution service endpoints for admin operations and enforce allowMutation flag server-side.
---

## a05-security-misconfiguration.md

[Medium] CORS origin: true uses permissive origin

File: packages/server/src/app.ts:21-26

Finding: CORS configured with origin true allowing any origin. This is acceptable in some test environments but risky in production.

Proposed Fix: Restrict allowed origins in production via configuration.
---

## a06-vulnerable-components.md

[High] Potential vulnerable dependencies

File: packages/server/package.json:12-27

Finding: Multiple server-side dependencies (express, jsonwebtoken, node-sql-parser, db drivers). Run npm audit to enumerate known CVEs.

Proposed Fix: Run dependency audit and update or patch vulnerable packages.
---

## a07-auth-failures.md

[Medium] Session cookie security depends on NODE_ENV

File: packages/server/src/routes/auth.routes.ts:49-56 and middleware at packages/server/src/middleware/auth.middleware.ts:6-14

Finding: Cookie secure flag is conditional on NODE_ENV. Ensure staging/prod set NODE_ENV and use secure cookies.

Proposed Fix: Enforce secure cookies for non-local environments and document deployment expectations.
---

## a08-integrity-failures.md

[Low] No obvious software integrity checks

File: repo root and deployment pipeline (no implementation found in code scan)

Finding: No code signing or update verification observed for bundled components.

Proposed Fix: Adopt signed releases and verify checksums during deployment.
---

## a09-logging-monitoring.md

[Medium] Potential sensitive data logging

File: packages/server/src/utils/logger.js and auth routes

Finding: Ensure logger does not emit sensitive fields (passwords, tokens). Some error handlers include error.message in logs.

Proposed Fix: Redact sensitive fields in logs and centralize logging filters.
---

## a10-ssrf.md

[Low] No direct SSRF sinks found in quick scan

File: search for http client usage in repo; none found in server package scan

Finding: No obvious SSRF vectors discovered in this pass.
---

## uncovered-concerns.md

Uncovered Concerns

- Verify there are no code paths that bypass sqlGuard and call adapters with raw concatenated SQL (check packages/server/src/services and adapters).
- Confirm env.JWT_SECRET is not checked into repository and is provided securely in deployment.
- Run npm audit and dependency checks in CI for both root and packages/server.
