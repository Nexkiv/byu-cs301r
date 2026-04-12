### [No Issues Found] SSRF (A10)

**Summary:** I searched the server codebase for any server-side HTTP/URI calls that accept user-controlled URLs or hostnames and found none. The server handles incoming HTTP and WebSocket requests and performs database operations and in-memory processing, but it does not make outbound HTTP requests based on client-provided URLs.

**Files/areas checked:**
- `chess/server` and `chess/client` sources for `HttpURLConnection`, `URI`, `URL`, `HttpClient` usage; client code constructs URIs to contact the server (expected), but server code does not perform outbound requests using user input.

**Recommendation:** If future features accept external URLs from users, apply strict URL validation and an allowlist for allowed hosts, and disallow requests to private IP ranges or metadata endpoints.

