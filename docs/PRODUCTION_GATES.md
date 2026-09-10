# Production Gates — Hussam NextGen

A gate is **GREEN** only when there is reproducible evidence, not a design statement.

| Gate | Status at v1.30 | Evidence required |
|---|---|---|
| Repository hygiene | GREEN | baseline audit + clean source tree |
| Unit/integration suite | GREEN | 139 passing tests |
| Python compilation | GREEN | compileall |
| Migration integrity | GREEN | fresh PostgreSQL Alembic + `alembic check` through `0015` |
| PostgreSQL production DB | PARTIAL | PostgreSQL 16.15 migration, constraints, and concurrency probes verified locally; production/staging performance evidence remains |
| Identity | BLOCKED | approved IdP, MFA/session/recovery tests, production configuration |
| Payments | PARTIAL | provider-agnostic lifecycle and HMAC webhook boundary tested; live provider sandbox, refunds, chargebacks, and reconciliation remain |
| Marketplace payouts | BLOCKED | verified payout rail + failure/retry/reconciliation evidence |
| Browser E2E | BLOCKED | deployed staging URL and automated browser journey |
| Security/SAST/SCA | PARTIAL | baseline scanner, dependency audit, request headers, and webhook authentication; external SAST/SCA and threat model still required |
| Secrets | PARTIAL | repository scan; production secret manager + rotation still required |
| Backups/restore | BLOCKED | tested backup and restore drill |
| Observability | PARTIAL | request correlation, structured request logs, health/readiness endpoints; metrics/traces/alerts/runbooks remain |
| Deployment/rollback | BLOCKED | immutable build + staged deploy + rollback drill |
| Abuse/rate limiting | BLOCKED | gateway/WAF/rate-limit controls and load/abuse tests |
| Legal/compliance | BLOCKED | marketplace/payment/identity operational review |

## Release rule

Do not label the platform “production ready” while any BLOCKED gate is unresolved.

## Minimum staging sequence

1. Provision PostgreSQL.
2. Configure production-grade identity.
3. Deploy immutable backend/frontend artifacts.
4. Run migrations against staging DB.
5. Execute API security and tenant-isolation tests.
6. Execute browser E2E business journey.
7. Connect payment sandbox and signed webhooks.
8. Execute logistics/COD/reconciliation scenarios.
9. Exercise backup/restore and rollback.
10. Enable monitoring and alerts.
11. Record evidence and promote only after all required gates are GREEN.
