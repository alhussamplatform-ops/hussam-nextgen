# Hussam NextGen v1.15 — Minimum Unified API

## Purpose
v1.15 is deliberately small: it exposes the existing production engines through one authenticated `/api/v1` boundary. It does not add a new business engine or storage layer.

## Authentication
Every business endpoint requires `Authorization: Bearer <JWT>`.
The JWT is verified at the API boundary, then the database resolves the active user, active tenant, and active membership. The tenant is never trusted from a request-body tenant field.

## API groups
- `/api/v1/inventory` — items, warehouses, movements, stock snapshot
- `/api/v1/sales` — sales orders and lifecycle
- `/api/v1/purchasing` — suppliers, purchase orders, confirmation
- `/api/v1/payments` — payment intents and provider attachment/processing
- `/api/v1/finance` — balanced journal posting
- `/api/v1/logistics` — shipment creation and status transitions
- `/api/v1/workflows` — definitions, instances, events
- `/api/v1/documents` — business documents, finalization, links
- `/api/v1/platform/manifest` — platform capability manifest

## Boundary rules
The API layer only translates HTTP requests into existing engine contracts. Business invariants remain inside the engines. No route accepts a client-supplied tenant identifier as authority.

## Intentionally not included
No new storage engine, AI orchestration, compiler, microservice split, or additional domain engine is part of v1.15.

## Release gate
The API package is unit/smoke tested locally. Real PostgreSQL, real identity provider, external payment providers, production deployment, and browser end-to-end testing remain production gates.
