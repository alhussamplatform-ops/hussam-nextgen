# v1.5 — Identity & Security Runtime

## Security path
JWT claims identify the user and requested tenant context, but they do NOT grant access by themselves.
The server resolves an active user, active tenant, and active tenant membership from the database.
RBAC permissions are resolved from membership -> roles -> permissions.

## Tenant isolation
- A requested tenant ID must match the authenticated tenant context.
- A tenant must be active.
- A membership must be active.
- Queries can be explicitly scoped from the server-derived context.
- Cross-tenant access is denied before domain logic.

## JWT
- HS256 verification is explicit.
- Algorithm confusion is rejected.
- Expiration is mandatory.
- Secrets shorter than 32 characters are rejected.
- JWT tenant_id is treated as a routing hint and is revalidated against persistent membership.

## Production gate
This package provides the security runtime contracts and database-backed resolution,
but a production deployment still needs a standards-compliant OIDC/JWKS provider,
key rotation, refresh/session policy, rate limiting, CSRF policy where applicable,
security headers, and full HTTP integration tests.


## Verification correction
The first generated test pass exposed a schema mismatch in the inherited User model (boolean `active`, string `id`). The tests and runtime were corrected to the actual model contract before release packaging. Fresh migration definitions were aligned to the same contract.
