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

The current Marketplace orchestration uses existing engine service boundaries. Cross-engine checkout operations use explicit transaction orchestration while preserving Finance, Inventory, and Commerce as the authoritative engines.

## Phase 2 checkout hardening

Marketplace checkout now owns an explicit orchestration transaction: Commerce can
defer its commit when called by checkout, the buyer cart is locked during the
operation, and Core `IdempotencyRecord` stores the tenant-scoped checkout result
when an `Idempotency-Key` is supplied. A failure rolls back the SalesOrder,
inventory reservation, Marketplace order, payout, outbox events, and idempotency
record created by that checkout.

PostgreSQL concurrency validation showed that duplicate requests with the same
key converge on one result, while different keys racing on the same cart resolve
to one checkout and one deterministic empty-cart rejection. SQLite tests do not
prove these row-locking results.
