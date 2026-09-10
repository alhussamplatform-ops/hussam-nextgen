# AI + HUS Foundation v1.23

## Decision
The legacy repositories are reference sources, not the runtime source of truth. The old platform explicitly documented HUS Compiler v6 as a six-stage pipeline — Boot, Parser, Validator, Resolver, Contract Injector, Generator — and exposed an AI Hub and compiler service. The legacy audit also warned that those services were monolithic and that AI inputs needed security restrictions. NextGen adopts the concepts while rebuilding them behind Sovereign Core boundaries.

## AI control plane
AI is advisory by default. A model/provider is never an authority over tenant data or financial state.

Flow:
`AI Provider -> AI Run -> Tool Proposal -> Policy/Approval -> Core Command -> Audit/Outbox`

Tool risks:
- `read`: can be executed without human approval after authorization.
- `mutation`: requires explicit approval before execution.
- `admin`: reserved for elevated governance and requires explicit approval.

Every run is tenant-scoped and hashes its input. Actions are persisted with risk, status and approval actor.

The provider interface is deliberately dependency-free. OpenAI/local/other providers can be adapters later; no provider is embedded in the Core.

## HUS Compiler
The first NextGen HUS compiler is declarative and deterministic. It does not execute generated code and has no network/filesystem execution path.

Stages:
1. Boot — input object boundary.
2. Parser — structured specification input.
3. Validator — schema, required fields, duplicates and supported values.
4. Resolver — map domains to approved shared engines.
5. Contract Injector — represented by the generated contract boundary.
6. Generator — deterministic JSON contract, never executable code.

Version `1.0` is intentionally narrow. It supports organizations, domains, workflows, policies and metadata. The generated contract can later become input to provisioning/configuration services.

## Security invariants
- tenant is derived from authenticated context.
- AI records cannot cross tenants.
- mutation/admin AI actions cannot become completed merely by model output.
- HUS compilation cannot execute arbitrary code.
- HUS output is declarative and deterministic.
- hashes use canonical JSON.
- all important lifecycle transitions emit outbox events.

## Legacy reuse
From `hosamahad57-collab/hussam-platform-v2`, we retain the conceptual six-stage HUS pipeline and the AI Hub/provider separation, but not its monolithic implementation. The repository audit specifically identifies `compiler_service.py` and `aihub.py` as large modules requiring isolation, and identifies risks around remote downloads/local paths in AI input handling.

The older `hussam-core-ai` repository is treated as a specification/constitution reference only; no legacy runtime is imported into NextGen.

## Production gates still separate
Real model-provider credentials, production identity, PostgreSQL staging, signed provider webhooks, concurrency, backups/restore, observability and deployment are still production gates. v1.23 does not claim those are complete.
