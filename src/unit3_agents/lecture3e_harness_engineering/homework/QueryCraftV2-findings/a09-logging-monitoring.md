[Medium] Potential sensitive data logging

File: packages/server/src/utils/logger.js and auth routes

Finding: Ensure logger does not emit sensitive fields (passwords, tokens). Some error handlers include error.message in logs.

Proposed Fix: Redact sensitive fields in logs and centralize logging filters.