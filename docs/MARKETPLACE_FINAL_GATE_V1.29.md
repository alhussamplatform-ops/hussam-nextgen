# Marketplace Final Gate v1.29

The Marketplace software domain is considered feature-complete for the current architecture. Before accepting real customers or real money, the following external gates must be executed and evidenced.

## 1. Identity and trust
- Production IdP/federation.
- MFA/passkeys and recovery.
- Seller identity/KYC workflow appropriate to the legal entity and operating jurisdictions.
- Account/session lifecycle and abuse controls.

## 2. Money movement
- Select payment and payout providers actually available to the operating legal entity.
- Signed webhook verification and replay protection.
- Payment/capture/refund/chargeback/reconciliation tests.
- Seller payout destination verification by the provider.
- Multi-currency and FX policy where applicable.
- Reconciliation between Payments, Finance, Marketplace payouts and external provider statements.

## 3. Commerce and logistics
- PostgreSQL concurrent checkout tests.
- Oversell race tests.
- Idempotent checkout/payment webhook/retry behavior.
- Trusted shipment event integration.
- Delivery failure/return/refund scenarios.
- Shipping rate source and quote expiration in production.

## 4. Trust & Safety
- Listing moderation operations.
- Seller suspension/appeal operations.
- Fraud/risk/rate limits.
- Review and dispute abuse controls.
- PII retention/deletion policy.
- Audit review and incident response.

## 5. Platform operations
- Staging environment matching production architecture.
- PostgreSQL migration/upgrade rehearsal.
- Backup and restore drill.
- Observability, metrics, traces and alerts.
- Deployment/rollback rehearsal.
- Browser E2E on staging.
- Load/failure-injection tests.

## Release rule
No external gate may be marked passed merely because the application code exists. Each gate requires an executable test, environment evidence, or an approved operational/legal artifact.
