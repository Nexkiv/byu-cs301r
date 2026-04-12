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

### [Low] Password hashing uses BCrypt (correct)
**File:** `chess/server/src/main/java/service/Service.java:45-47`.

BCrypt is used for password hashing; ensure the cost factor is configurable for operational tuning.

