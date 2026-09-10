# HUS Operational Compiler v1.24

v1.24 turns HUS from a deterministic compiler foundation into an operational contract lifecycle.

## Lifecycle
1. Compile a tenant-scoped declarative specification.
2. Validate root/domain/workflow/policy structure.
3. Resolve domains, capabilities and workflow actions against an allow-listed engine registry.
4. Inject declarative bindings only; no executable code is generated.
5. Persist the compiled contract and hashes.
6. Activate one contract per tenant; activating a new contract supersedes the previous active contract.

## Security boundary
HUS never executes generated code, shell commands, dynamic imports, downloads, or network instructions. The generated artifact is a declarative contract consumed by application services.

## API
- `POST /api/v1/hus/compile`
- `GET /api/v1/hus/active`
- `GET /api/v1/hus/compilations/{id}`
- `POST /api/v1/hus/compilations/{id}/activate`

All routes require the existing authenticated tenant context.
