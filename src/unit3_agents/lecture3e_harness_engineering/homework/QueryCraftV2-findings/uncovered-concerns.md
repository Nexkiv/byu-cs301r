Uncovered Concerns

- Verify there are no code paths that bypass sqlGuard and call adapters with raw concatenated SQL (check packages/server/src/services and adapters).
- Confirm env.JWT_SECRET is not checked into repository and is provided securely in deployment.
- Run npm audit and dependency checks in CI for both root and packages/server.
