# Hussam NextGen v1.13 — Documents & Business Records

The Documents Engine is a tenant-scoped registry for business records and immutable content versions.

## Boundaries
- The engine stores business metadata, lifecycle, version hashes and external/object-storage keys.
- It does **not** become the blob-storage provider; bytes belong in an object/file storage adapter.
- Domain engines remain authoritative for their own facts.
- A document can link to any aggregate through an explicit typed relation.

## Lifecycle
`draft -> finalized -> void`

Draft documents may receive versions. Finalized documents cannot receive new versions. Voiding is a lifecycle fact, not physical deletion.

## Integrity
- SHA-256 content digest and exact byte size are recorded per version.
- Versions are immutable records.
- References are unique per tenant.
- Links are idempotent by tenant/document/aggregate/relation.
- All reads and mutations require tenant identity at the engine boundary.
- Lifecycle/version/link changes emit transactional outbox events.

## Production boundary
Object storage, malware scanning, content-disposition/download authorization, encryption-at-rest configuration, retention/legal-hold policy and real PostgreSQL concurrency remain deployment/release gates. This package deliberately does not pretend those external systems are implemented.
