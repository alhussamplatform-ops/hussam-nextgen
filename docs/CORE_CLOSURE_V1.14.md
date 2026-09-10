# Core Closure v1.14

This release closes the Sovereign Core boundary without adding a new business engine.

## Scope
- One authenticated-context boundary: verified JWT claims -> active DB user/tenant/membership.
- Tenant override remains forbidden.
- Database remains authoritative for active user, active tenant, and active membership.
- Outbox duplicate handling uses a nested transaction so a duplicate event does not roll back the caller's outer transaction.
- Platform/API version markers are aligned to `1.14.0`.

## Deliberately not included
- No new Storage/File Engine.
- No new business domain.
- No AI expansion.
- No Marketplace expansion.
- No microservices split.

## Next step
Build the minimum unified application API over the engines already present in v1.13, then test one real end-to-end business flow.
