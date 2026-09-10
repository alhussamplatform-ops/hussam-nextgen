# Release v1.27.0

## Scope
Marketplace Core over the existing Hussam NextGen v1.26 foundation.

## Implemented
- multi-seller seller profiles
- catalog/categories/listings
- product and service listing types
- buyer profiles/addresses
- carts and multi-seller checkout
- marketplace orders and immutable line snapshots
- seller-funded commission facts
- payout hold/eligibility/paid lifecycle
- reviews and disputes
- authenticated seller/buyer APIs
- public published catalog
- Arabic operations console Marketplace surface
- migration `0013_marketplace`

## Verification
- 119 pytest tests passed
- Python compileall passed
- fresh Alembic upgrade from empty database through `0013_marketplace` passed
- `alembic check` passed with no new operations
- source diff check passed

## Explicit non-claims
This release does not claim live provider credentials, real signed payment webhooks, regulated seller KYC, live payout rails, production PostgreSQL concurrency, browser E2E against staging, or production deployment.
