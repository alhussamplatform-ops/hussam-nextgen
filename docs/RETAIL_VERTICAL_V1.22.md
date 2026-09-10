# Retail Vertical v1.22

The first concrete vertical adapter for Hussam NextGen.

## Boundary
Retail owns sector-specific facts: customers, retail product identity (SKU/barcode/category), retail price points, and register shifts.

Retail does **not** become the source of truth for inventory, sales orders, payments, or accounting. Those remain owned by Inventory, Commerce, Payments, and Finance engines.

## Supported foundation
- tenant-scoped customers
- tenant-scoped product profile
- SKU/barcode uniqueness
- multi-currency retail prices with exact Decimal values
- register opening/closing shifts
- only one open shift per register; historical closed shifts remain allowed
- transactional outbox events
- authenticated API routes
- tenant isolation

## Business flow proven by the existing engine suite
Retail product -> Inventory receipt -> Sales order -> reservation -> fulfillment -> payment -> settlement -> shipment -> delivery -> accounting.

The vertical adapter deliberately composes existing engines instead of duplicating their source-of-truth logic.

## Not claimed yet
- POS hardware integration
- fiscal/tax rules
- real payment-provider certification
- offline synchronization
- production PostgreSQL/concurrency certification
- browser E2E against production infrastructure

These are production gates, not reasons to duplicate domain engines.
