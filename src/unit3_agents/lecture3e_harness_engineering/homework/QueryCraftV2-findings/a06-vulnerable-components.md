[High] Potential vulnerable dependencies

File: packages/server/package.json:12-27

Finding: Multiple server-side dependencies (express, jsonwebtoken, node-sql-parser, db drivers). Run npm audit to enumerate known CVEs.

Proposed Fix: Run dependency audit and update or patch vulnerable packages.