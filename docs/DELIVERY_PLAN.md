# NextGen Delivery Plan

## Completed foundations
- v1.0: Core contracts, money, tenant context, domain registry.
- v1.1: Persistent tenant/user/membership boundary; journal and inventory movement persistence.
- v1.2: Finance lifecycle (fiscal periods, posting gate, reversal links, exchange rates) and inventory reservations.

## Next engineering gates
1. PostgreSQL schema + Alembic migrations with clean-database integration tests.
2. Authentication adapter + session/token verification + policy/RBAC engine.
3. Full audit/event outbox with transactional guarantees.
4. Inventory availability/concurrency controls and warehouse topology.
5. Commerce order lifecycle and procurement.
6. Payment adapter contract + signed webhook verification + reconciliation.
7. Logistics lifecycle and geographic model.
8. First vertical: Retail/Grocery, implemented only through shared contracts.
9. Web/API/Android clients.
10. AI orchestration and HUS Compiler only after deterministic core boundaries are proven.

## Release rule
A version is not production-ready merely because unit tests pass. Production gates require migration tests, integration tests, security tests, concurrency tests, observability, backup/restore evidence, and deployment smoke tests.
