# v1.4 — Production Persistence

## Goal
Move the Sovereign Core from a test-oriented in-memory database harness toward
migration-controlled PostgreSQL persistence.

## Implemented
- DATABASE_URL is required by the production database configuration.
- PostgreSQL URLs are normalized to the psycopg SQLAlchemy driver.
- Session transactions commit atomically and rollback on failure.
- Alembic environment and an initial explicit core migration are present.
- Governance tables and core finance/inventory tables are represented in the migration.
- Transactional outbox repository writes events in the caller's transaction.

## Critical boundary
`Base.metadata.create_all()` remains available only in the existing foundation/test harness.
Production startup must use Alembic migrations and must not mutate schema implicitly.

## Verification status
The package is syntactically validated and the existing application test suite must remain green.
A real PostgreSQL integration run is still a release gate because this execution environment
does not guarantee a PostgreSQL server.
