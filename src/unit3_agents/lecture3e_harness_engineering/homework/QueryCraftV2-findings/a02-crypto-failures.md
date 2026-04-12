[Low] JWT secret and bcrypt present

File: packages/server/src/routes/auth.routes.ts:38-47

Finding: JWT is signed using env.JWT_SECRET; confirm secret management and rotation. bcrypt used for passwords, which is appropriate.

Proposed Fix: Use strong managed secret (vault) and rotate tokens periodically.