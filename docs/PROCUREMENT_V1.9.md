# Hussam NextGen v1.9 — Procurement Production Engine

Procurement is the authoritative workflow for supplier purchasing. It does not own inventory balances or accounting balances.

## Lifecycle

`Draft → Confirmed → Partially Received → Received`

or `Draft/Confirmed → Cancelled`.

## Receiving

A posted receipt atomically creates:

1. purchase receipt + receipt lines;
2. inventory `IN` movements;
3. cumulative received quantities on PO lines;
4. outbox event.

The operation rolls back as one transaction on validation, uniqueness, or accounting failure.

## Accounting boundary

Receiving can post an optional double-entry journal in the same database transaction:

- Debit: configured inventory account
- Credit: configured accounts-payable account

Finance remains the authoritative accounting engine; Procurement only supplies the business fact.

## Security/integrity

- Every supplier, PO, line, and receipt is tenant-scoped.
- References are unique per tenant.
- Receipt quantity cannot exceed the remaining ordered quantity.
- A receipt cannot target a line from another tenant/order.
- Exact `Numeric(20,4)` quantities and monetary values.
- PostgreSQL row locking is used for purchase order/line mutation paths; live concurrent PostgreSQL validation remains a release gate until a real PostgreSQL environment is exercised.
