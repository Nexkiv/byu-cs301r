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

