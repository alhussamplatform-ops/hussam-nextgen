# Hussam NextGen v1.11 — Logistics & Shipment Engine

Logistics owns shipment lifecycle, tracking facts, and cash-on-delivery collection facts. It does not post authoritative finance entries or impersonate a payment provider.

Flow: fulfilled order -> shipment ready -> picked_up -> in_transit -> out_for_delivery -> delivered; failure/return/cancellation paths are explicit.

Guarantees: tenant scoping, unique shipment/tracking references, immutable tracking assignment, idempotent tracking events, exact Decimal COD, COD only after delivery, and atomic persistence with transactional outbox events.

PostgreSQL row locking is used on shipment mutation paths through `FOR UPDATE` where applicable. SQLite tests do not prove multi-process concurrency; a live PostgreSQL concurrency gate remains required.
