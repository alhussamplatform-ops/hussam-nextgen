# Architecture Baseline v1.30

## Canonical dependency direction

```text
Clients
  ↓
API Gateway / HTTP Boundary
  ↓
Identity + Tenant Context
  ↓
Domain Application Services
  ↓
Shared Engines
  ↓
Sovereign Core
  ↓
Persistence
```

Domain engines must not become alternative authorities for Core-owned facts.

## Sovereign Core authorities

Identity, organizations/tenants, memberships, authorization, policies, audit, events/outbox, idempotency, lifecycle, configuration, money/data context.

## Shared engine authorities

Finance, inventory, commerce, procurement, payments, logistics, workflow, documents.

## Vertical examples

Retail and Marketplace are vertical/product layers over the shared engines.

## AI boundary

```text
Provider → AI Run → Tool Proposal → Risk/Authorization → Approval → Core Command → Audit/Outbox
```

AI may observe and recommend; it does not become a hidden authority for money, stock, identity, permissions, or audit.

## HUS boundary

HUS is a deterministic declarative compiler/control plane. It must not execute arbitrary shell, dynamic imports, downloads, or uncontrolled filesystem/network actions.

## v1.30 review note

The current Marketplace orchestration uses existing engine service boundaries. Cross-engine operations that span independently committed transactions remain a production hardening item; future work should prefer explicit transaction orchestration or a durable saga/outbox pattern rather than duplicating domain authorities.
