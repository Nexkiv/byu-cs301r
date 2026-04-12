### [Medium] Unverified third-party JARs and potential deserialization risks

**Files reviewed:** `chess/server/pom.xml` (systemPath dependency), JSON deserialization sites (Gson usage across server and shared modules)

**Findings & Explanation:**
- The server POM references a system-scoped JAR `passoff-dependencies.jar` via `systemPath` (`chess/server/pom.xml` lines ~46-56). System-scoped dependencies bypass normal repository resolution and may be supplied externally; ensure this artifact is obtained from a trusted source and its integrity is verified.
- Gson is used to deserialize JSON into application types (e.g., `UserData`, `ChessGame`, `MakeMoveCommand`, `UserGameCommand`). While Gson itself does not perform Java native deserialization (it maps JSON to POJOs), deserializing complex types without schema validation can allow malformed or unexpected data to be accepted. If the deserialized types are later used in ways that execute code paths (reflection or polymorphic dispatch), this could be risky.

**Proposed Refactor / Remediation:**
- Avoid `system` scoped dependencies in production builds; publish artifacts to an internal artifact repository and utilize checksums/signatures.
- Apply strict JSON schema validation at boundaries (e.g., require exact field sets, types, and limits) before mapping to internal types.
- For highly sensitive data flows, include integrity checks (signatures or HMAC) on persisted payloads where applicable.

