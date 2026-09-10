# v1.17 — Business Operations

This release adds the smallest operational surface over the existing engines. It does not add a new business engine.

## Surface
- `/console` — minimal operator console.
- `/docs` — FastAPI API documentation.
- `/api/v1/session` — authenticated session context.
- Purchase receipt, payment webhook/capture/settlement lifecycle endpoints complete the existing business flow at the API boundary.

## Boundary
The UI is a thin client. Business rules remain in the existing Core and engines. No new database migration is introduced.

## Production gates
Real identity/token issuance, PostgreSQL, real payment provider credentials/webhook signatures, and deployment infrastructure remain production gates.
