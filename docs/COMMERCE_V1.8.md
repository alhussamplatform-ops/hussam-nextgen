# Commerce Production Engine v1.8

## Scope

v1.8 introduces a tenant-scoped sales-order lifecycle without making Commerce the source of truth for stock.

`Draft -> Confirmed -> Fulfilled`

Cancellation is allowed from `Draft` or `Confirmed` and releases active reservations.

## Invariants

- Every order and line is tenant-scoped.
- Order reference is unique within a tenant.
- Currency and exact Decimal monetary values are explicit.
- A draft cannot be confirmed without sufficient available inventory unless the warehouse explicitly allows negative stock.
- Confirmation reserves all lines as one database transaction.
- Fulfillment consumes reservations and creates authoritative inventory OUT movements in the same database transaction.
- A fulfilled order cannot be fulfilled again.
- Cross-tenant order access is rejected.
- Order events are written to the transactional outbox.

## Boundary

Commerce owns order intent and lifecycle. Inventory remains authoritative for stock movements and balances. Finance remains authoritative for accounting. Payment and shipment providers are intentionally deferred to later engines.

## Production gate

SQLite tests validate deterministic invariants. PostgreSQL live integration, multi-process concurrency, and end-to-end payment/shipment integration remain release gates.
