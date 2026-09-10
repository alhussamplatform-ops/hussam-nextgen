# Canonical Architecture

```text
Clients
  -> API Gateway
  -> Identity / Tenant Context
  -> Domain Application Services
  -> Shared Engines
       Finance | Inventory | Commerce | Payments | Logistics | Workflow | Reporting
  -> Sovereign Core
       Policy | Audit | Events | Idempotency | Money | Lifecycle | Registry | Config
  -> Persistence
```

### Dependency boundaries
- Domains may import shared engine contracts and core contracts.
- Shared engines may import Core only.
- Core never imports a vertical domain.
- AI may observe and propose through contracts; it cannot bypass authorization or accounting invariants.

### First production sequence
1. PostgreSQL + migrations + configuration.
2. Identity, membership and tenant isolation.
3. Finance with immutable double-entry lifecycle.
4. Inventory movement/reservation.
5. Commerce and procurement.
6. Payments + reconciliation adapters.
7. Logistics.
8. First verticals.
9. AI orchestration.
10. HUS Compiler.
11. Web/Android hardening and launch gates.
