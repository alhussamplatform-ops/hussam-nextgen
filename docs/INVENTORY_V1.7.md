# Hussam NextGen v1.7 — Inventory Production Engine

## Contract
Inventory is movement-authoritative. On-hand and available stock are derived from immutable movement records and active reservations.

## Supported lifecycle
Purchase/receipt -> IN movement -> reservation -> OUT/fulfillment -> delivery/settlement integration.
Transfers are represented by one transfer record with source and destination warehouses and are interpreted as -quantity at source and +quantity at destination.

## Invariants
- tenant-scoped item/warehouse/movement/reservation access
- Decimal/Numeric(20,4) quantities
- quantity > 0
- explicit IN/OUT/TRANSFER directions
- unique movement and reservation references per tenant
- negative stock denied by default
- reservation consumes available stock, not physical on-hand
- release restores availability
- fulfillment creates the OUT movement and closes the reservation atomically
- inventory changes emit transactional outbox events
- no stored mutable balance is treated as authoritative

## Concurrency
The service performs availability checks inside the transaction and keeps the data model compatible with row-locking on PostgreSQL. A live PostgreSQL concurrent-writer test remains a production release gate; SQLite unit tests do not prove database-level locking.

## Next gate
Production-grade API commands, authentication integration, PostgreSQL migration execution, row-lock/concurrency tests, and end-to-end order/shipment integration.
