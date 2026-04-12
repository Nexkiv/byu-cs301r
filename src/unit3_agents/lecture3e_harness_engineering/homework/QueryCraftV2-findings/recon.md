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
