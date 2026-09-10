# Pre-AI / Pre-HUS Gate — v1.22

This document is the architectural gate before building AI and the HUS Compiler.

## What is now stable enough to build on
- Sovereign Core tenant/user/membership boundary
- RBAC/policy/lifecycle/audit/idempotency/outbox foundations
- Finance as accounting source of truth
- Inventory as stock source of truth
- Commerce as sales-order source of truth
- Procurement as purchase/receipt source of truth
- Payments as provider-agnostic payment lifecycle
- Logistics as shipment/tracking/COD fact source
- Workflow as deterministic coordination layer
- Documents as business-record registry
- first vertical adapter: Retail / Grocery
- authenticated tenant-scoped API and operational console
- versioned Alembic migration chain through `0009_retail_vertical`

## Rules for AI
AI may observe, analyze, recommend and orchestrate, but cannot bypass tenant authorization, policy, accounting invariants, inventory invariants, lifecycle rules, or audit/outbox boundaries. AI mutations must call deterministic application commands.

## Rules for HUS Compiler
HUS must compile declarative organization/domain/workflow specifications into validated contracts/configuration. It must not generate an alternative database authority or bypass Core/Engine boundaries. Compilation must be deterministic, versioned, inspectable and sandboxed.

## Remaining production gates
These are infrastructure/certification gates, not architectural reasons to restart:
- real PostgreSQL staging
- real identity provider
- signed payment-provider webhooks and credentials
- concurrency/load tests on PostgreSQL
- backup/restore drill
- observability/alerts
- production deployment and rollback
- browser E2E against deployed staging

## Decision
The platform is **architecturally ready to begin AI and HUS design/implementation in parallel with production certification**, while those production gates remain explicitly unclaimed until proven.
