# v1.30 Baseline Evidence Record

This record separates checks performed in the release workspace from gates that need external infrastructure.

## Bootstrap verification record

Verified in the official `hussam-nextgen` workspace after unpacking the supplied
baseline archive:

## Repository checks

- Baseline audit: **PASS**
- Python compilation: **PASS**
- Automated suite: **138 passed, 0 failed**
- Fresh Alembic chain: **PASS** on PostgreSQL 16.15 and SQLite, `0001` → `0015_marketplace_trust_ai_integration`
- Alembic drift check: **PASS**, no new upgrade operations detected
- Release tree secret/runtime artifact audit: **PASS**
- Editable package installation: **PASS** after explicit setuptools discovery
	was added for the `app*` package namespace.
- Dependency consistency: **PASS** with `pip check`.
- Dependency vulnerability audit: **PASS** with the locked patched releases.
- PostgreSQL checkout concurrency: **PASS**, same-key replay converges to one
	order and different keys serialize on the cart lock.
- Checkout rollback injection: **PASS**, no SalesOrder, reservation, payout,
	Marketplace order, or idempotency record remains after failure.
- Payment webhook signature boundary: **PASS**, HMAC verification is required
	at the HTTP boundary.

## Reproducibility assets

- `requirements.lock`
- `Dockerfile`
- `compose.staging.yml`
- `.env.example`
- `.github/workflows/ci.yml`
- `scripts/release_check.sh`

The supplied ZIP was used only as the import artifact and is not the source of
truth in the repository tree.

## Evidence limitation

The local release workspace does not constitute proof of production infrastructure. PostgreSQL production concurrency, external identity, payment providers, signed webhooks, payout rails, browser E2E, backup/restore, observability, deployment rollback, abuse controls, and legal/compliance remain explicit gates.
