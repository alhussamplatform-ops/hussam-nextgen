# Hussam NextGen v1.30.0 — Repository & Production Baseline

**Hussam Yemeni Sovereign Platform — NextGen** is a sovereign, modular, multi-tenant operating platform for economic and institutional activity.

## Architecture

`domain → shared engine → Sovereign Core`

Core authorities include identity, tenant/membership context, authorization, policy, audit, events/outbox, idempotency, lifecycle, configuration, and money/data invariants. Shared engines provide finance, inventory, commerce, procurement, payments, logistics, workflow, and documents. Retail and Marketplace are vertical/product layers over those shared authorities.

### Engines

Shared engines provide finance, inventory, commerce, procurement, payments,
logistics, workflow, and documents. They enforce the cross-domain invariants
owned by the Sovereign Core.

### Domains

Retail and Marketplace are domain/product layers over shared authorities. The
`app/domains` registry remains intentionally thin; domain implementations live
in engines and API boundaries.

### AI/HUS

The provider-neutral AI control plane and bounded HUS declarative compiler are
downstream of identity, policy, audit, accounting, and inventory controls. AI
cannot bypass those invariants.

## Current capabilities

- Multi-tenant identity context and authorization boundary.
- Exact Decimal/Numeric financial values and double-entry finance.
- Inventory, reservations, sales, procurement, payments, logistics, workflow, and business documents.
- Retail vertical.
- Multi-seller marketplace with seller verification, listing moderation, shipping quotes, orders, reviews, disputes, payout controls, and AI read metrics.
- Provider-neutral AI control plane and bounded HUS declarative compiler.
- Arabic RTL operational console.

## v1.30 baseline

This release prepares the repository for the **official independent NextGen GitHub repository**. It adds repository hygiene, environment contract, reproducibility snapshot, CI, baseline static checks, security/contribution policy, architecture baseline, and explicit production gates.

### Verified in the release build

- **139 tests passed**.
- Python compilation passed.
- Fresh Alembic migration through `0015_marketplace_trust_ai_integration` passed on PostgreSQL 16.15 and SQLite validation paths.
- `alembic check` passed.
- Migration chain audit passed.
- Repository secret/runtime artifact audit passed.
- Authenticated payment webhook boundary, request correlation/security headers,
  database readiness, and PostgreSQL checkout concurrency validation passed.

### Important: production status

**v1.30 is not a production-readiness declaration.** Real PostgreSQL, production identity, signed payment webhooks, payout rails, browser E2E, backups/restore, observability, deployment/rollback, rate limiting, and legal/compliance gates still require external staging/production evidence.

See:
- `docs/V1_30_REPOSITORY_PRODUCTION_BASELINE.md`
- `docs/ARCHITECTURE_BASELINE_V1_30.md`
- `docs/PRODUCTION_GATES.md`
- `docs/RELEASE_V1_30.md`
- `SECURITY.md`
- `CONTRIBUTING.md`

## Development

Python 3.11+ is required. Install the locked validation dependencies and the
editable project with:

```bash
python -m pip install -r requirements.lock
python -m pip install -e '.[test]'
```

The unpacked source tree is the repository source of truth. Release ZIP files
are distribution artifacts and are ignored by Git.

## Testing

Run `make baseline`, `make compile`, `make test`, and `make migrate-check` for
the local gates. CI also runs `pip check` and `pip-audit`.

## Production gates

Repository checks are reproducible locally, but external gates remain required
before production promotion. PostgreSQL staging, identity, signed payment
webhooks and payouts, browser E2E, backups/restore, observability,
deployment/rollback, abuse controls, and legal/compliance evidence are tracked
in `docs/PRODUCTION_GATES.md`. This baseline is not a Production Ready claim.

## Official repository policy

The legacy `hussam-platform-v2` repository remains **reference/legacy**. The new independent `hussam-nextgen` repository becomes the NextGen source of truth after publication.

Do not commit credentials, `.env`, local databases, logs, virtual environments, caches, or generated runtime artifacts.
