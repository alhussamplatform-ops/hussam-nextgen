# Sovereign Core Persistence — v1.2

The foundation now contains the first persistent core plus deterministic lifecycle controls.

### Identity boundary
- Tenant and User records.
- Unique user/tenant membership.
- Active tenant and active membership required for authorization.

### Finance boundary
- Double-entry journal + lines.
- Tenant/reference uniqueness.
- Exact `Numeric(20,4)` monetary storage.
- Fiscal periods with closed-period posting rejection.
- Reversal creates a separate journal linked to the original; original remains posted.
- Exchange-rate records are tenant scoped and positive.

### Inventory boundary
- Movements are the source of stock history.
- Exact `Numeric(20,4)` quantities.
- Reservations are tenant scoped and cannot exceed computed available stock in the foundation service.
- Reservation release changes lifecycle state; it does not delete history.

### Explicitly not claimed
Production PostgreSQL/Alembic deployment, authentication-provider integration, distributed concurrency guarantees, payment-provider integrations, full warehouse topology, and production observability are later gates.
