[Medium] Broad privileges for query execution

File: packages/server/src/routes/query.routes.ts:40-58

Finding: Student/admin modes differ; ensure role separation and least privilege for execution contexts.

Proposed Fix: Separate execution service endpoints for admin operations and enforce allowMutation flag server-side.