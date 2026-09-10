# Hussam NextGen v1.3 — Core Governance

This increment strengthens the Sovereign Core before vertical features.

## Implemented contracts
- Permission/policy enforcement: an operation may require an explicit permission set.
- Lifecycle: explicit state machine with closed terminal state.
- Domain events: stable event identity and timestamp, tenant-bound.
- Idempotency: a key cannot be reused for a different request fingerprint.
- Persistence structures: roles, permissions, membership-role assignments, and transactional outbox records.

## Architectural rule
Domain services must not bypass these governance boundaries. Finance, inventory, commerce,
payments, and logistics should call Core contracts rather than implementing their own authorization,
event, idempotency, or lifecycle rules.

## Still required before production
- Alembic/PostgreSQL migration path
- real JWT/OIDC request middleware and server-derived tenant context
- transactional outbox write in the same DB transaction as authoritative mutations
- persistent idempotency middleware with response replay
- full RBAC administration APIs and policy evaluation
- concurrency/locking tests
- integration, security, backup/restore and deployment evidence
