# Production Gates — Hussam NextGen

A gate is **GREEN** only when there is reproducible evidence, not a design statement.

| Gate | Status at v1.30 | Evidence required |
|---|---|---|
| Repository hygiene | GREEN | baseline audit + clean source tree |
| Unit/integration suite | GREEN | 129 passing tests |
| Python compilation | GREEN | compileall |
| Migration integrity | GREEN* | fresh Alembic + `alembic check` (*SQLite validation path) |
| PostgreSQL production DB | BLOCKED | staging/prod PostgreSQL migration + concurrency tests |
| Identity | BLOCKED | approved IdP, MFA/session/recovery tests, production configuration |
| Payments | BLOCKED | provider sandbox + signed webhooks + reconciliation/refund/chargeback tests |
| Marketplace payouts | BLOCKED | verified payout rail + failure/retry/reconciliation evidence |
| Browser E2E | BLOCKED | deployed staging URL and automated browser journey |
| Security/SAST/SCA | PARTIAL | baseline scanner + CI; external SAST/SCA and threat model still required |
| Secrets | PARTIAL | repository scan; production secret manager + rotation still required |
| Backups/restore | BLOCKED | tested backup and restore drill |
| Observability | BLOCKED | logs/metrics/traces/alerts + runbooks |
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
