### [No Issues Found] Injection (A03)

**Summary:** I reviewed the code paths where user input reaches persistent storage and system commands. The primary data storage layer (`MySqlDataAccess`) uses `PreparedStatement` with parameter binding for all CRUD operations (see for example `getUser`, `createUser`, `createGame`, and `updateGameData`). The web layer deserializes JSON using Gson and passes structured objects into business logic; there are no string concatenations of user input into SQL statements or OS commands in the request handling paths.

**Files and checks performed:**
- `chess/server/src/main/java/dataaccess/MySqlDataAccess.java` — Verified use of parameterized `PreparedStatement` for reads and writes (lines ~78-107, 146-186, 206-216). No SQL concatenation with user-provided values detected.
- `chess/server/src/main/java/dataaccess/DatabaseManager.java` — `createDatabase()` builds a `CREATE DATABASE IF NOT EXISTS ` + `DATABASE_NAME` (DatabaseManager.java: lines 36-47). `DATABASE_NAME` comes from `db.properties` (resource), not directly from external requests; ensure that deployment does not use untrusted values here. This is a configuration-time string concatenation, not a request-time SQL injection exposure.
- `chess/server/src/main/java/service/*` and `chess/server/src/main/java/server/Server.java` — JSON bodies are parsed with Gson into typed objects before use; no evidence of template or command injection.

**Conclusion:** No direct injection vulnerabilities were found in the request handling → DB paths. The code uses prepared statements appropriately and does not concatenate user-controlled input into SQL statements at runtime.

**Recommendation (defensive):**
- Treat `db.properties` as a sensitive configuration and ensure it is not influenced by user input. For defense-in-depth, avoid building SQL DDL by concatenating arbitrary resource values; instead validate expected database name characters or construct the DDL via safer library calls.

