### [Critical] Unauthenticated endpoint to clear the database

**File:** `chess/server/src/main/java/server/Server.java:42-50` (route registration) and `chess/server/src/main/java/server/Server.java:69-73` (handler).

**Vulnerable Code:**
```
// Route registration (Server.java)
Spark.delete("/db", this::clearData);

// Handler (Server.java)
private Object clearData(Request request, Response response) throws ResponseException {
    service.clear();
    response.status(200);
    return "";
}
```

**Explanation:**
The `DELETE /db` endpoint calls `service.clear()` which truncates and/or drops database tables (see `MySqlDataAccess.clear()` / `eraseDatabase()`). This route is registered without any authentication or authorization checks. Any unauthenticated client who can reach the server can invoke `DELETE /db` and wipe the application's data store. This is a destructive operation that should be strongly restricted.

This meets the definition of Broken Access Control because a sensitive operation is exposed to unauthenticated or unauthorized clients.

**Proposed Refactor:**
- Remove the endpoint from production code, or limit activation to test/development only (e.g., controlled by an environment flag).
- Enforce a server-side authorization check that requires a valid, privileged token (an 'admin' role) before executing destructive actions.

Example refactor (conceptual) to gate the handler by a required admin token or env flag:
```
// Registration: only enable in non-production/testing or when enabled by env
if (Boolean.parseBoolean(System.getenv().getOrDefault("ENABLE_DB_RESET", "false"))) {
    Spark.delete("/db", this::clearData);
}

// Handler: verify admin credentials server-side before performing the operation
private Object clearData(Request request, Response response) throws ResponseException {
    String authToken = request.headers("Authorization");
    if (!service.validAdminToken(authToken)) {
        response.status(401);
        return "{\"message\": \"Error: unauthorized\"}";
    }
    service.clear();
    response.status(200);
    return "";
}
```

**Rationale:**
- Removing or gating the endpoint prevents accidental exposure of destructive functionality in production environments.
- Checking server-side for a valid admin token (and/or a dedicated role field stored in the DB) enforces that only authorized operators can perform data-destructive actions. This is a structural change: add explicit authorization checks and an admin capability in the authentication model rather than relying on network-level obscurity.

---

## Deferred to Other Auditors
- The presence of opaque auth tokens and lack of expiration may be relevant to `auditors/auth-failures`. File: `chess/server/src/main/java/service/Service.java:49-51` (token generation) and `chess/server/src/main/java/service/Service.java:145-152` (token validation).

