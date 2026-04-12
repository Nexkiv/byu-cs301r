[Medium] CORS origin: true uses permissive origin

File: packages/server/src/app.ts:21-26

Finding: CORS configured with origin true allowing any origin. This is acceptable in some test environments but risky in production.

Proposed Fix: Restrict allowed origins in production via configuration.