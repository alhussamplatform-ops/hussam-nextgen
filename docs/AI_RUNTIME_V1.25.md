# AI Runtime v1.25

v1.25 adds an explicit read-tool execution boundary to the AI control plane.

## Rule
Model providers produce suggestions. They never receive direct database mutation authority.

A read action must pass:
`tenant + actor -> run -> registered tool -> approved READ action -> deterministic handler -> audit/outbox`

Mutation/admin actions remain proposal/approval gated and are not dynamically executable. A future mutation executor must be an explicit command registry over existing domain services.

## Built-in deterministic read tools
- `platform.overview`
- `retail.overview`
- `inventory.stock`
- `sales.summary`

Unknown or merely database-registered read tools cannot execute until a server-side handler is explicitly registered.

## Provider boundary
`AIProvider` remains a provider-neutral protocol. Provider configuration is deliberately not bundled into the core release; credentials and provider-specific networking belong in deployment configuration/adapters.
