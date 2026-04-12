### [High] Missing role separation and unprotected administrative operations

**File:** `chess/server/src/main/java/server/Server.java:42-50` (routes) and `chess/server/src/main/java/service/Service.java:135-139` (auth creation)

**Vulnerable Code:**
```
// Server registers administrative route with no role checks
Spark.delete("/db", this::clearData);

// Service issues opaque tokens with no role or privilege metadata
private AuthData createAuthData(String username) {
    AuthData userAuthData = new AuthData(username, generateToken());
    dataAccess.createAuthData(userAuthData);
    return userAuthData;
}
```

**Explanation:**
- There is no role or privilege model in the authentication system. Any authenticated user receives an auth token that grants access to normal actions, but administrative/destructive operations (like `/db`) are not protected by role checks. This design conflates authentication and authorization and fails the separation-of-privilege principle.

**Proposed Refactor:**
- Introduce role metadata for accounts (e.g., `role` column on `user` or `authentication`) and require role checks for administrative endpoints.
- Remove dangerous admin endpoints from public server code or gate them behind feature flags and strict admin-only checks.

**Refactor Example:**
```
// Add role into AuthData and DB, set role at registration for admin accounts only
// In clearData handler:
String authToken = request.headers("Authorization");
if (!service.userHasRole(authToken, "admin")) {
    response.status(403);
    return "{\"message\": \"Forbidden\"}";
}
service.clear();
```

**Rationale:**
- Adding explicit roles and server-side enforcement prevents privilege escalation and accidental exposure of destructive functionality.

---

### [Medium] Missing rate limiting, request-size caps, and TLS enforcement

**Files/areas reviewed:** `chess/server/src/main/java/server/Server.java` (routes), `chess/server/src/main/java/service/websocket/*` (connections)

**Findings & Explanation:**
- There are no rate-limiting or throttling controls on HTTP endpoints or WebSocket handlers; an attacker may attempt DoS or brute-force token guessing.
- Request bodies are parsed with Gson with no size checks — large or deeply nested JSON could cause resource exhaustion.
- Server binds to a port via `Spark.port(desiredPort)` with no TLS configuration in code; TLS should be enforced at the deployment/ingress layer or via Spark TLS configuration.

**Proposed Refactor / Controls:**
- Introduce middleware filters for rate limiting (IP- or token-based) and request size limits at the web server level.
- Validate and cap JSON body sizes, and validate payload shapes (schema validation) before deserialization.
- Enforce HTTPS at the ingress or configure Spark with TLS and reject non-TLS connections.

