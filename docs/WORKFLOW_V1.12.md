# Hussam NextGen v1.12 — Integration & Workflow Engine

The workflow engine is a deterministic orchestration layer. It owns workflow state, transition history, tasks and correlation; domain engines remain authoritative for finance, inventory, commerce, procurement, payments and logistics.

## Rules
- Every definition is tenant-scoped and versioned.
- Instances bind to one immutable definition version.
- Transitions are explicit and event-driven.
- Transition event IDs are idempotent per tenant.
- Terminal states cannot be mutated through normal transitions.
- Workflow mutations emit transactional outbox events.
- Workflow does not invent financial approval, stock, payment or shipment facts.
- Domain commands must still pass their own authorization, invariants and audit rules.

## Example
`start -> reserve -> fulfill -> ship -> collect -> complete`

Each step declares accepted event types and a target step. Later releases can add durable command handlers, retries and saga compensation without weakening these boundaries.
