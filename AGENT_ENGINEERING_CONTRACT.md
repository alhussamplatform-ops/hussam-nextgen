# Hussam NextGen Agent Engineering Contract

**Status:** Permanent engineering contract for AI and coding agents
**Baseline:** V1.30 source of truth
**Repository:** `hussam-nextgen`

This document governs future AI agents, coding agents, and human-assisted
automation working in the Hussam NextGen repository. The repository is the
authoritative source. The legacy `hussam-platform-v2` repository may be used
only for comparison or verification and must not be mixed into this codebase.

## 1. Platform Identity

Hussam NextGen is a sovereign, modular, multi-tenant digital operating platform.
It is initially Yemen-first in operational context, language, and market
assumptions, but it is not Yemen-locked. Its boundaries must support controlled
regional and international expansion without weakening tenant, financial,
security, or governance invariants.

"Sovereign" means that core identity, tenant context, authorization, policy,
auditing, lifecycle, accounting, inventory, and operational contracts remain
under explicit platform control. External providers are adapters and evidence
sources, not replacements for platform authority.

## 2. Architecture

The mandatory dependency direction is:

```text
Domain -> Shared Engine -> Sovereign Core
```

The repository also exposes this runtime boundary:

```text
Client -> API Boundary -> Identity/Tenant Context -> Domain Services
       -> Shared Engines -> Sovereign Core -> Persistence
```

Domains must not directly depend on unrelated domains. Cross-domain workflows
must compose shared services or explicit orchestration boundaries. Shared
engines must not duplicate or replace Core authority. A vertical composes
existing engines; it does not create a parallel accounting, payment, identity,
or inventory authority.

Agents must preserve these boundaries when adding code, tests, migrations,
configuration, or documentation.

## 3. Sovereign Core

The Sovereign Core owns the platform facts and controls that every domain and
engine must respect:

- **Identity:** authenticated actor identity and authentication context.
- **Users:** user records, active state, and actor references.
- **Organizations and tenants:** tenant identity, status, ownership context,
  and isolation boundary.
- **Memberships:** user-to-tenant membership, active state, and tenant role
  context.
- **Authorization/RBAC:** server-side permission decisions and role bindings.
- **Policies:** platform and tenant rules, approvals, and allowed actions.
- **Audit:** durable records of sensitive mutations and their actor, tenant,
  subject, action, and time.
- **Events:** domain and engine facts emitted from committed operations.
- **Outbox:** durable event delivery boundary for external or asynchronous
  processing.
- **Idempotency:** repeat-request protection and request/response identity.
- **Lifecycle:** valid state transitions, activation, suspension, completion,
  reversal, and terminal states.
- **Configuration:** environment and operational configuration without exposing
  secrets in source.
- **Contracts:** shared typed structures, invariants, and stable boundaries.
- **Tenant context:** the tenant scope attached to every tenant-owned read and
  mutation.
- **Security boundaries:** authentication, authorization, tenant isolation,
  validation, provider boundaries, and audit requirements.

A lower layer must not silently bypass a Core-owned fact. If a proposed change
needs a new authority, stop and obtain explicit architecture approval.

## 4. Shared Engines

The current shared engines are:

| Engine | Authoritative responsibility |
| --- | --- |
| Finance | Fiscal periods, journals, journal lines, posting validation, balanced double-entry facts, reconciliation, and reversal workflows. |
| Inventory | Items, warehouses, movement-based stock, reservations, fulfillment, negative-stock policy, and stock concurrency controls. |
| Commerce | Sales order and order-line lifecycle and commerce transaction coordination. |
| Procurement | Purchasing and procurement lifecycle, suppliers, and procurement production flows. |
| Payments | Payment intents, provider-facing payment state, webhooks, settlements, and payment reconciliation boundaries. |
| Logistics | Shipment and delivery lifecycle, shipping operations, and logistics state. |
| Workflow | Operational workflow definitions, steps, triggers, and state progression. |
| Documents | Business document creation and document lifecycle. |

An engine owns its bounded operational facts and invariants. It must reuse Core
identity, tenant context, authorization, audit, idempotency, lifecycle, and
outbox facilities. An engine must not copy another engine's authority merely to
simplify a local flow.

## 5. Current Verticals

The current vertical/product layers are:

- **Retail:** retail-specific composition over shared commerce, inventory,
  finance, payments, logistics, documents, and governance capabilities.
- **Marketplace:** multi-seller catalog and marketplace orchestration over
  identity, commerce, inventory, payments, logistics, finance, and outbox
  boundaries.

Verticals compose existing shared engines rather than duplicating them. A
vertical may own its catalog, presentation, and domain workflow facts, but the
shared engine remains authoritative for the underlying accounting, stock,
payment, shipment, document, or lifecycle fact.

## 6. AI and HUS

AI is a provider-neutral control plane. The required command boundary is:

```text
AI Provider -> AI Run -> Tool -> Risk/Authorization
             -> Approval when required -> Core Command
             -> Transaction -> Audit -> Outbox
```

AI may observe, recommend, and propose bounded actions. AI must never bypass:

- authorization;
- tenant boundaries;
- policies and approval requirements;
- accounting invariants;
- inventory invariants;
- auditability; or
- lifecycle rules.

AI actions must use the same server-side security boundaries and Core commands
as normal application commands. Read actions, mutations, and administrative
actions must remain explicitly risk-classified. Provider output is untrusted
external data and must be validated before it can influence a command.

HUS is the deterministic six-stage declarative compiler:

```text
Boot -> Parser -> Validator -> Resolver -> Contract Injector -> Generator
```

The current compiler is declarative and deterministic. It validates allow-listed
roots, domains, workflows, actions, capabilities, policies, and produces a
canonical contract with hashes and bindings. HUS must not execute arbitrary
shell commands, dynamic imports, downloads, uncontrolled filesystem access, or
uncontrolled network access. HUS output is a contract for bounded execution,
not an alternative authority.

## 7. Financial Invariants

Finance is the authoritative accounting source of truth. Financial code must
preserve all of the following:

- Money uses exact `Decimal`/database `Numeric` representations, never binary
  floating-point accounting.
- Every accounting fact is tenant-scoped and tenant-isolated.
- Accounting uses double-entry journals.
- Every posted journal has balanced debit and credit totals with positive value.
- Posting is allowed only in exactly one open fiscal period.
- Posted facts are immutable after posting.
- Corrections use a reversal journal rather than destructive editing.
- Downstream domains may request or reference accounting facts, but may not
  become a second accounting authority.

Any change that weakens these invariants is a data-integrity change and requires
explicit review, tests, and architecture approval.

## 8. Inventory Invariants

Inventory is authoritative for stock state and must preserve:

- Movement records are the source of truth for on-hand quantity.
- Reservations have an explicit lifecycle: active, released, or fulfilled.
- Negative stock is denied by policy unless the warehouse explicitly allows it.
- Items, warehouses, movements, reservations, and availability are tenant
  isolated.
- Stock mutations require concurrency-safe locking in PostgreSQL, including
  row-level warehouse locking where applicable.
- SQLite is useful for deterministic validation but does not prove production
  concurrency behavior.
- Inventory mutations emit durable outbox events and remain idempotency-aware.

Agents must not replace movement history with a mutable aggregate shortcut or
claim SQLite tests prove PostgreSQL concurrency safety.

## 9. Marketplace Boundary

Marketplace responsibilities include:

- seller registration and verification;
- listing moderation and catalog lifecycle;
- buyer profiles, carts, and order lifecycle;
- multi-seller checkout;
- shipping quotes;
- payment coordination;
- commission calculation and marketplace payout state;
- disputes and returns; and
- reviews and buyer-facing marketplace interactions.

Marketplace must not become a second accounting or payment authority. Finance
owns accounting facts. Payments owns provider payment facts and reconciliation.
Inventory owns stock and reservations. Commerce owns sales-order facts.
Marketplace orchestration must call or compose those authorities and must emit
appropriate audit/outbox evidence.

## 10. Security Rules

Every agent and every change must follow these rules:

- Never commit secrets, `.env` files, credentials, private keys, tokens, or
  production configuration values.
- Never hard-code production credentials.
- Tenant isolation is mandatory on every tenant-owned read and mutation.
- Authorization is server-side and cannot depend on UI behavior.
- External provider data must be authenticated where applicable, parsed, and
  validated against expected tenant, amount, currency, state, and identity.
- Webhooks must be authenticated and idempotent.
- Sensitive mutations must be auditable with actor, tenant, action, subject, and
  outcome context.
- Production authentication must use an appropriate production identity
  provider; the current development authentication boundary is not production
  evidence.
- AI actions must pass the same authorization, tenant, policy, audit,
  lifecycle, accounting, and inventory boundaries as normal commands.

If a security or data-integrity ambiguity is discovered, stop and report it
before implementing a speculative resolution.

## 11. Database and Migration Rules

- Every schema change requires an Alembic migration.
- Migrations should be reversible where practical and must preserve data
  intentionally when reversal is not safe.
- Never modify a historical migration after release; add a new migration.
- Production PostgreSQL is the final database authority.
- SQLite is a development and validation path only unless explicitly approved
  for another purpose.
- A migration change requires fresh-upgrade validation and Alembic drift checks.
- Migration ordering, heads, tenant constraints, indexes, and data semantics
  must be reviewed before release.

## 12. Engineering Rules for AI Agents

Agents must:

1. Inspect the existing code, contracts, tests, and documentation before
   changing anything.
2. Reuse existing contracts, services, Core controls, and engine boundaries.
3. Avoid duplicate engines, duplicate authorities, and parallel models for the
   same fact.
4. Avoid speculative features and unrelated cleanup.
5. Avoid architecture rewrites without explicit approval.
6. Run the relevant focused tests and static checks for every change.
7. Run baseline, security, migration, and dependency checks when the change
   touches those surfaces or before a release.
8. Report failures, warnings, environment limitations, and unverified gates
   honestly.
9. Never claim production readiness without reproducible evidence.
10. Stop when a security or data-integrity ambiguity is discovered.

No agent may use this contract as permission to add product features, change
business logic, change migrations, alter existing API contracts, or create a
fake implementation. The current repository remains authoritative.

## 13. Git Rules

- Make small, coherent commits.
- Use descriptive commit messages.
- Never commit secrets or generated artifacts.
- Never force-push `main`.
- Do not rewrite published history.
- Do not silently revert unrelated work.
- Review `git status`, `git diff`, and `git diff --check` before committing.
- Push only the intended commit and verify the remote branch afterward.

## 14. Production Readiness

These terms are not interchangeable:

- **Implemented:** code exists in the repository.
- **Tested:** automated tests or a documented local check passed.
- **Staging verified:** behavior passed against configured staging
  infrastructure and representative integrations.
- **Production verified:** production infrastructure, controls, evidence, and
  operational procedures passed review.
- **Production ready:** all required gates are evidenced and the release has a
  documented GO decision.

At the V1.30 source-of-truth baseline, repository hygiene, the automated suite,
Python compilation, SQLite migration integrity, Alembic drift checks, and local
dependency checks are implemented/tested. They are not proof of production
readiness.

The following production gates remain incomplete or externally dependent:

- PostgreSQL staging/production migration, concurrency, and performance
  validation;
- production identity provider, MFA, sessions, recovery, and identity policy;
- real payment provider sandbox/production integration, authenticated signed
  webhooks, reconciliation, refunds, chargebacks, and payout rails;
- browser end-to-end journeys against a deployed staging environment;
- external SAST/SCA, threat modeling, and security review;
- production secret manager integration and key rotation;
- tested backups, restore, disaster recovery, and rollback;
- centralized logs, metrics, traces, alerts, and operational runbooks;
- immutable deployment, supply-chain attestation, and deployment rollback;
- gateway/WAF/rate limiting, abuse, load, and DDoS controls; and
- marketplace, payment, identity, KYC, fraud, legal, and compliance review.

No agent or document may label V1.30 Production Ready while any required gate
remains unverified.

## 15. Current Roadmap

The controlled order of work is:

A. V1.30 source-of-truth closure
B. PostgreSQL staging and concurrency validation
C. Production identity and security
D. Real payment provider integrations
E. Browser E2E
F. Production operations, observability, backups, and deployment
G. Threat model and security review
H. Final production GO/NO-GO
I. Controlled vertical expansion

A later step must not be used to conceal an unresolved gate in an earlier step.
Any change that changes this order requires explicit platform-owner approval.

## Agent Acknowledgement

Before changing the repository, an agent should be able to answer:

- Which existing authority owns this fact?
- Which tenant, authorization, lifecycle, audit, and idempotency boundaries
  apply?
- Which existing contract or service can be reused?
- What is the smallest change and the focused check that can disprove it?
- Which gates remain unverified after the change?

If those answers are unclear, inspect more or stop and report the ambiguity.
