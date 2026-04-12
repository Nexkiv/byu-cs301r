[Medium] Missing explicit role checks on admin routes

File: packages/server/src/app.ts:48

Finding: admin routes are mounted at /api/admin but review should verify role enforcement in handlers and role.middleware usage.

Proposed Fix: Ensure role.middleware enforces admin role at route level and in service entry points.