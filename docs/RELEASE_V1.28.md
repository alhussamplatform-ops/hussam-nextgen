# Hussam NextGen v1.28.0 — Marketplace Completion & Hardening

## Scope

This release closes important Marketplace launch-boundary gaps without introducing a second commerce, inventory, payment, or finance source of truth.

### Included
- Seller verification lifecycle and `platform_admin` review boundary.
- Public marketplace visibility requires an active, approved seller.
- Server-owned shipping rates and expiring shipping quotes.
- Checkout rejects arbitrary client-supplied non-zero shipping fees.
- Payment intent is attached to the marketplace order at creation.
- Payment synchronization is available after authoritative Payments capture.
- Paid/processing orders cannot be directly cancelled; refund/dispute workflow is required.
- Buyer favorites.
- Return-request lifecycle record after delivery.
- Reusable buyer cart after checkout; cart items are cleared after immutable orders are created.
- Alembic metadata now imports Marketplace and AI Intelligence models so schema drift is detected.

## Verification

- 125 automated tests passed.
- Python compileall passed.
- Fresh SQLite migration from empty database through `0014_marketplace_completion` passed.
- `alembic check` passed against the freshly upgraded database.
- ZIP integrity verified.

## Production gates still external

Real payment-provider signatures, payout rails, identity proofing, PostgreSQL concurrency/load testing, backup/restore, observability, deployment/rollback, browser E2E on staging, moderation operations, fraud/risk controls, and legal/privacy controls require real infrastructure and credentials. They are not falsely marked complete by this release.
