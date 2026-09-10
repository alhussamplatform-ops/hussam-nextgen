# v1.6 — Finance Production Engine

The finance engine is now treated as an authoritative ledger boundary.

## Invariants
- Double-entry journals must balance exactly using Decimal arithmetic.
- Each line is debit OR credit, never both.
- Zero-value lines are rejected.
- References are unique per tenant.
- Posting requires an open fiscal period.
- A journal cannot be posted into a closed or ambiguous period.
- Reversals create a new journal and a JournalLink; the original journal remains unchanged.
- Reversal is tenant-scoped.
- Account balances are calculated from journal lines rather than mutable balance fields.
- Currency is attached to the journal and included in balance calculations.

## Concurrency / production gate
PostgreSQL deployment must add appropriate transaction isolation/locking around
fiscal-period closure and duplicate-reference races. This package tests deterministic
invariants but does not claim a live multi-worker PostgreSQL concurrency proof.
