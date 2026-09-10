# Release v1.30.0 — Repository & Production Baseline

## Base

v1.29.0 Marketplace Final.

## Release objective

Prepare the official NextGen repository and define an evidence-driven production path without falsely declaring production readiness.

## Verified checks

- `python scripts/baseline_audit.py`
- `python -m compileall -q app alembic tests`
- `python -m pytest -q` → 129 passed
- fresh Alembic upgrade → 0015
- `alembic check` → clean
- release archive integrity verified

## Explicit remaining gates

See `docs/PRODUCTION_GATES.md`.

## Release artifact

The release archive should be generated from the clean repository tree after all checks pass. The official GitHub repository should publish the source tree and attach the immutable archive as a release asset.
