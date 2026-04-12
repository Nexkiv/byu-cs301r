[High] SQL injection risks if raw SQL bypasses sqlGuard

File: packages/server/src/services/queryExecutor.ts and packages/server/src/adapters/*.ts
Finding: SQL is parsed and filtered in sqlGuard, but any code paths that pass user input directly to adapters or use string concatenation should be reviewed.

Proposed Fix: Require parameterized queries at adapter layer and centralize sanitization.