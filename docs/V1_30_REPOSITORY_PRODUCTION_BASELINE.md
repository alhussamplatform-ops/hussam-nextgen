# v1.30 — Repository & Production Baseline

## Purpose

v1.30 is the **last repository-preparation release before the official NextGen GitHub repository becomes the source of truth**. It converts the v1.29 functional release into a clean, auditable, reproducible engineering repository and establishes explicit production gates.

## What was verified in this release

- 129 automated tests pass.
- Python source compilation passes.
- Alembic fresh upgrade through `0015_marketplace_trust_ai_integration` passes on the available SQLite validation path.
- `alembic check` passes on the available SQLite validation path.
- Migration chain is statically checked for a single head and complete ancestry.
- Repository contains no committed `.env`, local database, private-key, log, virtual-environment, or cache artifacts.
- Baseline secret-pattern scan is clean.
- Repository architecture checks are present and domain boundaries are reviewed.
- CI is defined for repeatable validation.
- Editable installation is explicit and limited to the `app*` package namespace
	so CI cannot fail on accidental flat-layout package discovery.
- The locked validation dependencies pass `pip check` and `pip-audit` in this
	bootstrap environment.

## What this release does NOT prove

The following require infrastructure or external credentials and therefore cannot honestly be marked complete from the repository alone:

1. Production PostgreSQL availability, migrations, and concurrency behavior.
2. Production identity provider, MFA/session policy, account recovery, and identity proofing.
3. Real payment-provider onboarding, signed webhooks, reconciliation, refunds, chargebacks, and payout rails.
4. Browser end-to-end testing against a deployed staging environment.
5. Rate limiting, WAF/API gateway controls, DDoS posture, and operational abuse controls.
6. Secret-manager integration and production key rotation.
7. Backup, restore, disaster-recovery, and rollback drills.
8. Centralized logs, metrics, tracing, alerting, and on-call runbooks.
9. Container/image supply-chain signing and deployment attestations.
10. Marketplace legal/compliance, seller KYC/verification operations, fraud/risk operations, and financial-provider obligations.

## Repository rules

The official repository should contain the unpacked source tree, not only a release ZIP. The ZIP may be retained as a release artifact/checksum.

Never upload:
- `.env` or credentials
- database files
- logs
- `.venv` / `venv`
- `__pycache__`
- `.pytest_cache`
- build artifacts not intentionally released

## Source-of-truth rule

- Legacy `hussam-platform-v2`: reference/legacy only.
- `hussam-nextgen`: official NextGen source of truth after initial repository publication.
- Release ZIPs: immutable distribution artifacts, not the development source of truth.

## Exit criterion

v1.30 repository baseline is complete when all repository checks are green. Production readiness remains blocked until the external gates in `docs/PRODUCTION_GATES.md` are evidenced.
