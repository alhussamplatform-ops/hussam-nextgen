# Marketplace Production Gate v1.27

The Marketplace domain is implemented and tested, but these are required before claiming live production readiness:

## Identity
- Replace development JWT issuer with a production IdP/federation flow.
- Establish seller verification/identity proofing appropriate to the operating jurisdiction.
- Enforce account recovery, MFA/passkeys and session lifecycle in the production identity layer.

## Payments and payouts
- Select providers that are actually available for the platform's legal entity and operating countries.
- Implement signed webhook verification and replay protection.
- Connect seller payout destinations only after provider verification.
- Implement real refund/chargeback flows and reconcile them with the marketplace payout ledger.
- Test multi-currency and currency conversion rules.

## Commerce/logistics
- Run PostgreSQL concurrency tests for cart/checkout/reservation.
- Test oversell races under concurrent checkout.
- Add real shipping rate/zone contracts before charging variable delivery fees.
- Connect delivered shipment facts to payout eligibility only from trusted logistics events.

## Trust and safety
- Seller moderation and verification.
- Listing moderation.
- Fraud/risk rules and rate limits.
- Abuse controls for checkout, reviews and disputes.
- Privacy/PII retention and deletion policy.

## Platform operations
- PostgreSQL staging and production.
- Backup/restore proof.
- Observability and alerting.
- Deployment/rollback.
- Browser E2E on staging.
- Load and failure-injection testing.

## Security baseline
OWASP API Security Top 10 2023 should be used as the minimum review checklist, especially BOLA, broken authentication, property/function authorization, unrestricted sensitive business flows, security misconfiguration and improper API inventory.
