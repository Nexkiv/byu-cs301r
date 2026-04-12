# OWASP Security Audit Report


## Executive Summary


Total findings: 13


- Critical: 1

- High: 2

- Medium: 6

- Low: 2



Categories audited:

- A01: Broken Access Control -- 1 finding

- A02: Cryptographic Failures -- 1 finding

- A03: Injection -- 0 findings

- A04: Insecure Design -- 2 findings

- A05: Security Misconfiguration -- 1 finding

- A06: Vulnerable and Outdated Components -- 1 finding

- A07: Authentication Failures -- 1 finding

- A08: Software and Data Integrity Failures -- 1 finding

- A09: Security Logging and Monitoring Failures -- 1 finding

- A10: Server-Side Request Forgery -- 0 findings


## Codebase Overview


# Codebase Reconnaissance

## Languages and Frameworks
- Java (modules: `shared`, `server`, `client`). See `chess/pom.xml` and module POMs. (chess/pom.xml: lines 1-20).
- Spark Java web framework (routes defined in `server/Server.java`). (chess/server/pom.xml: lines 30-48).
- Google Gson for JSON (used across server and websocket). (chess/pom.xml: lines 11-18; chess/server/pom.xml: lines 1-40).
- Jetty / WebSocket annotations used in server websocket handler. (chess/server/src/main/java/service/websocket/WebSocketHandler.java:1-14).
- BCrypt (`org.mindrot:jbcrypt`) for password hashing. (chess/server/pom.xml: lines 49-56).

## Entry Points
- HTTP endpoints (Spark) registered in `chess/server/src/main/java/server/Server.java`.
  - Route registration: `Spark.port(...)`, `Spark.staticFiles.location("web")`, `Spark.webSocket("/ws", ...)`, and HTTP endpoints. (Server.java: lines 35-50).
  - HTTP endpoints and handlers (with exact handlers):
    - `DELETE /db` -> `clearData` (Server.java: lines 42-44, 69-73).
    - `POST /user` -> `registerUser` (Server.java: lines 44, 75-86).
    - `POST /session` -> `login` (Server.java: lines 45, 88-99).
    - `DELETE /session` -> `logout` (Server.java: lines 46, 102-110).
    - `POST /game` -> `createGame` (Server.java: lines 47, 113-129).
    - `PUT /game` -> `joinGame` (Server.java: lines 48, 131-151).
    - `GET /game` -> `listGames` (Server.java: lines 49, 153-163).
- WebSocket endpoint at `/ws` backed by `WebSocketHandler` (chess/server/src/main/java/server/Server.java: line 40; handler at chess/server/src/main/java/service/websocket/WebSocketHandler.java: lines 26-40).
- Static files served from resource path `web` (Server.java: line 38).

## Data Flows
- HTTP request bodies are deserialized with Gson directly into records such as `model.UserData` or `JsonObject` (Server.java: lines 75-77, 88-91, 115-116, 133-135).
  - Example: `registerUser` deserializes `request.body()` into `UserData` then passes to `Service.register`. (Server.java: line 76 and 80).
- Service layer (`chess/server/src/main/java/service/Service.java`) handles business logic and interacts with `DataAccess` (Service.java: lines 13-18, 28-40).
  - Passwords are hashed during registration (`hashPassword` uses BCrypt). (Service.java: lines 34-39, 45-47).
  - Auth tokens generated with `UUID.randomUUID()` and persisted via DataAccess. (Service.java: lines 49-51, 135-139).
- DataAccess implementations persist data to MySQL (or in-memory fallback). `MySqlDataAccess` configures tables and uses PreparedStatements for DB operations (chess/server/src/main/java/dataaccess/MySqlDataAccess.java: lines 17-26, 19-29, 31-40, 41-51, 78-88, 103-107, 110-118, 139-151, 171-179).

## Authentication and Authorization
- Authentication model: token-based (opaque UUID tokens).
  - Tokens are generated in `Service.createAuthData` using `UUID.randomUUID()` and stored in `authentication` table. (Service.java: lines 49-51, 135-139; MySqlDataAccess.java: lines 31-39, 110-118).
  - HTTP endpoints check tokens by reading the `Authorization` header and calling service methods which validate token presence in DB (Server.java: lines 102-115, 131-139, 153-156; Service.validAuthToken: Service.java: lines 145-152).
  - WebSocket messages contain an `authToken` field inside JSON commands and are validated in `WebSocketHandler.getConnection` via `dataAccess.getAuthData(authToken)`. (WebSocketHandler.java: lines 36-41, 61-69).
- No explicit token expiration or revocation policy beyond deletion on logout (`dataAccess.deleteAuth(authToken)`). (Service.successfulLogout: Service.java: lines 71-77; MySqlDataAccess.deleteAuth: lines 139-143).

## Data Storage
- Database: MySQL via `DatabaseManager.getConnection()` (used by `MySqlDataAccess`). Database schema creation strings are in `MySqlDataAccess.createStatements` (MySqlDataAccess.java: lines 19-51).
  - `user` table stores `username`, `password` (TEXT), `email`. (MySqlDataAccess.java: lines 21-28, 23-25).
  - `authentication` table stores `username`, `authToken`. (MySqlDataAccess.java: lines 31-39).
  - `game` table stores `gameJson` and player usernames. (MySqlDataAccess.java: lines 41-50).
- Potential sensitive data: password hashes stored in `user.password` column (MySqlDataAccess.java: lines 23-25); auth tokens stored in `authentication.authToken` (lines 33-35).

## Dependencies (security-relevant)
- `com.google.code.gson:gson:2.10.1` — JSON parsing/deserialization used on all endpoints (chess/pom.xml: lines 11-18).
- `com.sparkjava:spark-core:2.9.3` — HTTP routing framework (chess/server/pom.xml: lines 34-38).
- `org.mindrot:jbcrypt:0.4` — password hashing (chess/server/pom.xml: lines 49-56).
- `mysql:mysql-connector-java:8.0.30` — DB connector (chess/server/pom.xml: lines 23-28).
- `org.slf4j:slf4j-simple` — logging (chess/server/pom.xml: lines 29-33).

## Potential Concerns
- Authorization header handling uses the raw header string as token; no `Bearer` scheme enforced and no validation of header format before use (Server.java: lines 102-115, 131-139). Risk: malformed headers or accidental logging could leak tokens.
- Auth tokens are opaque UUIDs with no expiration. No sliding expiry or short TTL. (Service.generateToken: Service.java: lines 49-51; createAuthData: 135-139).
- WebSocket authentication relies on tokens sent inside JSON messages; if connections are logged or the client stores tokens insecurely, tokens may be exposed. (WebSocketHandler.java: lines 36-41, 61-69).
- No rate limiting, no CSRF protection for the HTTP endpoints exposed (server module has no middleware shown for rate limiting or CSRF). (Server.java: overall routing lines 35-50).
- SQL schema definitions and usage appear to use parameterized PreparedStatements (good). However the `CREATE TABLE` uses column name `password` as `TEXT` — ensure the application stores and treats this field as a hash (Service.hashPassword uses BCrypt; verify all user creation paths go through Service). (MySqlDataAccess.createStatements: lines 21-29; Service.register: lines 34-39).




## Critical Findings



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


## High Findings



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

### [High] Session tokens lack expiry, rotation, and brute-force protections

**Files:** `chess/server/src/main/java/service/Service.java:49-51` (token gen), `chess/server/src/main/java/service/Service.java:53-59` (login), `chess/server/src/main/java/server/Server.java:88-99` (login endpoint)

**Vulnerable Code:**
```
// Login flow (Server.java)
var user = SERIALIZER.fromJson(request.body(), UserData.class);
var auth = service.login(user);
return auth.toJson();

// Token generation (Service.java)
private String generateToken() {
    return UUID.randomUUID().toString();
}
```

**Explanation:**
- Tokens are generated and issued without expiry or rotation. Multiple active tokens can exist for a single user (login creates a new token without revoking previous tokens). If a token is stolen, it remains valid until explicitly deleted (logout) or removed.
- There is no brute-force protection: repeated failed login attempts are not throttled or blocked. Attackers can attempt credential stuffing or brute-force guessing without server-side rate limiting.
- Logout simply deletes a single token (Service.deleteAuth) but does not rotate other tokens that may have been issued.

**Proposed Refactor:**
- Add token expiry timestamps and enforce expiry at validation time. Consider short-lived access tokens with refresh tokens where refresh tokens are stored and rotated.
- On login, consider rotating tokens and invalidating existing active tokens, or issue short-lived tokens with refresh tokens.
- Add rate-limiting or progressive delays to the login endpoint; consider account lockout or CAPTCHA after repeated failed attempts.

**Example (conceptual):**
```
// On token issue: set expiry = now + 15 minutes; store hashed token and expiry
// On validation: reject expired tokens
// On login: rotate existing tokens or limit concurrent sessions per account
```

**Rationale:**
- Token expiry and rotation reduce the attack window for stolen credentials.
- Rate limiting reduces the feasibility of brute-force attacks against the login endpoint.

---


## Medium Findings



### [Medium] Auth tokens have no expiry and are stored verbatim in DB

**File:** `chess/server/src/main/java/service/Service.java:49-51` (token generation), `chess/server/src/main/java/service/Service.java:135-139` (createAuthData), `chess/server/src/main/java/dataaccess/MySqlDataAccess.java:31-39` (authentication table schema), `chess/server/src/main/java/dataaccess/MySqlDataAccess.java:110-118` (getAuthData)

**Vulnerable Code:**
```
// Token generation (Service.java)
private String generateToken() {
    return UUID.randomUUID().toString();
}

// Persisted as-is into DB (MySqlDataAccess.createAuthData)
String statement = "INSERT INTO authentication (username, authToken) VALUES (?, ?)";
int id = executeUpdate(statement, authData.username(), authData.authToken());
```

**Explanation:**
- Tokens are opaque UUIDs generated by `UUID.randomUUID()` and stored verbatim in the `authentication` table. There is no expiration or rotation. If an attacker gains read access to the DB, they can obtain valid session tokens and impersonate users.
- Storing tokens in plaintext increases the blast radius of a database compromise. Best practice is to store only a hashed form of tokens (similar to password storage) and compare tokens by hashing incoming token values.
- There is also no expiry or revocation policy (beyond manual deletion on logout), which increases the window for a stolen token to be abused.

**Proposed Refactor:**
- Add token TTL and persist an expiry timestamp alongside the token. Reject tokens that are expired during validation.
- Store a hashed version of the token (HMAC or bcrypt) in the DB rather than the raw token.
- Use a cryptographically-secure random byte sequence (or continue to use UUIDv4 which is built on SecureRandom) and perform explicit server-side expiry checks.

Example refactor (conceptual):
```
// When creating token:
byte[] raw = new byte[32];
SecureRandom.getInstanceStrong().nextBytes(raw);
String token = Base64.getUrlEncoder().withoutPadding().encodeToString(raw);
String hashed = HmacUtils.hmacSha256Hex(SECRET_KEY, token);
// store hashed token and expiry timestamp in DB
// return raw token to client

// When validating token:
String hashedIncoming = HmacUtils.hmacSha256Hex(SECRET_KEY, incomingToken);
AuthData auth = dataAccess.getAuthByHashedToken(hashedIncoming);
if (auth == null || auth.isExpired()) { deny }
```

**Rationale:**
- Hashing tokens in the DB prevents an attacker who reads the DB from directly using tokens to impersonate users. Token theft would require breaking the HMAC or guessing the token.
- TTL/expiry reduces the valid window for stolen tokens and is a standard defense-in-depth control.
- Using a server-held secret (HMAC) to hash tokens preserves the ability to validate without storing raw tokens.

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

### [Medium] Unrestricted administrative endpoint and absence of security headers/CORS controls

**Files/areas reviewed:** `chess/server/src/main/java/server/Server.java` (routes), top-level repo structure (presence of `.git`), logging dependency (chess/server/pom.xml: lines 29-33)

**Findings & Explanation:**
- `DELETE /db` is exposed without authorization checks (see findings/a01). This is both an access control and configuration issue: an administrative endpoint exists in application code and is reachable by default unless gated by environment.
- No explicit CORS policy or security headers are set in the web layer; Spark routes do not add `Content-Security-Policy`, `X-Content-Type-Options`, `X-Frame-Options`, or HSTS headers. Absence of these headers may increase risk when this service is deployed behind different front-ends or misconfigured proxies.
- The project uses `slf4j-simple` for logging. Ensure production logging is configured to avoid printing sensitive data (auth tokens, passwords) and that logs are forwarded to a secure aggregator.
- The repository contains a `.git` directory and IDE config (`.idea`) — ensure deployment artifacts do not include the repository metadata or developer files.

**Proposed Refactor / Remediation:**
- Remove or gate dev-only endpoints (`/db`) behind environment flags and admin-only checks. (See a01).
- Add middleware to set secure response headers for CSP, HSTS, X-Frame-Options, and X-Content-Type-Options.
- Configure CORS explicitly to allow only known origins and do not allow credentials for wildcard origins.
- Ensure `db.properties` and other secrets are injected from a secure secret manager or environment variables and are not checked into source control.
- Ensure build/deploy processes do not package `.git` or IDE configuration files into production artifacts.

### [Medium] Dependencies require vulnerability scanning and pinning verification

**Files reviewed:** `chess/pom.xml`, `chess/server/pom.xml` (dependencies and versions logged)

**Observed dependencies and versions:**
- `com.google.code.gson:gson:2.10.1` (chess/pom.xml)
- `com.sparkjava:spark-core:2.9.3` (chess/server/pom.xml)
- `mysql:mysql-connector-java:8.0.30` (chess/server/pom.xml)
- `org.mindrot:jbcrypt:0.4` (chess/server/pom.xml)
- `org.slf4j:slf4j-simple:1.7.36` (chess/server/pom.xml)

**Explanation:**
- The codebase declares explicit versions in Maven POMs, which is good for reproducible builds. However, dependency versions may contain known CVEs that change over time.

**Proposed Action:**
- Run an automated dependency vulnerability scanner (e.g., `mvn dependency:tree` then `mvn -Dorg.slf4j.simpleLogger.defaultLogLevel=warn -X` with OS tooling or use Snyk/OSS Index/Dependabot) to check for known CVEs affecting the above versions.
- Regularly update dependencies and test for breaking changes. If production security requirements exist, consider using a dependency policy that blocks known-severity CVEs.

**Rationale:**
- Vulnerabilities in third-party libraries are a common attack vector. Automated continuous scanning ensures quick detection and remediation of known issues.

### [Medium] Unverified third-party JARs and potential deserialization risks

**Files reviewed:** `chess/server/pom.xml` (systemPath dependency), JSON deserialization sites (Gson usage across server and shared modules)

**Findings & Explanation:**
- The server POM references a system-scoped JAR `passoff-dependencies.jar` via `systemPath` (`chess/server/pom.xml` lines ~46-56). System-scoped dependencies bypass normal repository resolution and may be supplied externally; ensure this artifact is obtained from a trusted source and its integrity is verified.
- Gson is used to deserialize JSON into application types (e.g., `UserData`, `ChessGame`, `MakeMoveCommand`, `UserGameCommand`). While Gson itself does not perform Java native deserialization (it maps JSON to POJOs), deserializing complex types without schema validation can allow malformed or unexpected data to be accepted. If the deserialized types are later used in ways that execute code paths (reflection or polymorphic dispatch), this could be risky.

**Proposed Refactor / Remediation:**
- Avoid `system` scoped dependencies in production builds; publish artifacts to an internal artifact repository and utilize checksums/signatures.
- Apply strict JSON schema validation at boundaries (e.g., require exact field sets, types, and limits) before mapping to internal types.
- For highly sensitive data flows, include integrity checks (signatures or HMAC) on persisted payloads where applicable.

### [Medium] Limited audit logging and lack of sensitive-data masking

**Files/areas reviewed:** `chess/server` (logging dependency), authentication and DB operations

**Findings & Explanation:**
- The codebase does not contain structured audit logging for authentication events (successful logins, failed logins, token creation, logout), administrative actions (database clear), or sensitive data access (game creation). There are `System.out` messages in client/test code and `Main` logs the server port, but no centralized audit log calls in the server business logic.
- I did not find explicit logging of tokens or passwords in server code — this is good. However, the logging backend is `slf4j-simple`, which uses a simple console logger by default; ensure production logging is configured to a secure aggregator and that no sensitive fields are logged.

**Proposed Refactor / Remediation:**
- Add structured audit logs at security-relevant events: authentication success/failure (include username, source IP, timestamp), token issuance/revocation, admin actions (who/when), and suspicious events. Do not log sensitive values such as raw tokens or passwords.
- Ensure logs are shipped securely (TLS to a log collector), have proper retention and rotation, and are protected from unauthorized access.
- Add alerting/monitoring rules for repeated failed login attempts, unexpected database clear events, and abnormal rates of token creation.


## Low Findings



### [Low] Password hashing in `Service.register` uses BCrypt (good)

**File:** `chess/server/src/main/java/service/Service.java:34-47` (password hashing)

**Vulnerable Code:**
```
UserData userWithHashedPassword = new UserData(userData.username(), hashPassword(userData.password()), userData.email());
private String hashPassword(String clearTextPassword) {
    return BCrypt.hashpw(clearTextPassword, BCrypt.gensalt());
}
```

**Explanation:**
BCrypt is used for password hashing, which is appropriate. Ensure bcrypt cost is tuned for production hardware.

**Proposed Refactor:**
- Make bcrypt cost (work factor) configurable via properties.
- Consider password peppering using a server-side secret if threat model requires protection against DB leaks plus stolen hashes.

### [Low] Password hashing uses BCrypt (correct)
**File:** `chess/server/src/main/java/service/Service.java:45-47`.

BCrypt is used for password hashing; ensure the cost factor is configurable for operational tuning.


## Unaddressed Concerns


- The presence of opaque auth tokens and lack of expiration may be relevant to `auditors/auth-failures`. File: `chess/server/src/main/java/service/Service.java:49-51` (token generation) and `chess/server/src/main/java/service/Service.java:145-152` (token validation).


## Uncovered Recon Concerns


# Uncovered Concerns

Recon entries not referenced by any auditor in this run.

- `WebSocketHandler.java: lines 36-41, 61-69` — Suspected category: [auth-failures]
- `- No rate limiting, no CSRF protection for the HTTP endpoints exposed (server module has no middleware shown for rate limiting or CSRF). (Server.java: overall routing lines 35-50).` — Suspected category: [insecure-design]
- `CREATE TABLE` — Suspected category: [other]
