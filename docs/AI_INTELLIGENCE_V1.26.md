# AI Intelligence v1.26

v1.26 turns the AI foundation into a bounded intelligence layer.

## Capabilities
- Tenant-scoped business snapshot derived from authoritative platform records.
- Deterministic operational insights for payments, logistics, inventory flow, and pending work.
- Explicit provider adapter for OpenAI-compatible APIs; provider credentials are not stored in Core tables.
- Tenant-scoped AI memory as structured records, not unrestricted model context.
- Bounded agent planning: plans and proposals only; no direct mutation.
- Evaluation records with scores constrained to 0..1.
- Explicit read tool `platform.business_snapshot`.

## Security boundary
AI cannot write to domain tables directly. Mutation remains:
AI proposal -> authorization/approval -> Core command -> audit/outbox.

No dynamic code execution, shell execution, remote downloads, generated imports, or filesystem access is permitted by the AI runtime.

## Production gates
Real model credentials, provider security review, rate limits, prompt/data policy, monitoring, model evaluation, PostgreSQL concurrency, backups, deployment, and browser E2E remain external production gates.
