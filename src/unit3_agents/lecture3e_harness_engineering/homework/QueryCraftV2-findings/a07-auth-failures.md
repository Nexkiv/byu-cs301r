[Medium] Session cookie security depends on NODE_ENV

File: packages/server/src/routes/auth.routes.ts:49-56 and middleware at packages/server/src/middleware/auth.middleware.ts:6-14

Finding: Cookie secure flag is conditional on NODE_ENV. Ensure staging/prod set NODE_ENV and use secure cookies.

Proposed Fix: Enforce secure cookies for non-local environments and document deployment expectations.