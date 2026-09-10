# Hussam NextGen v1.10 — Payments & Settlement Engine

## Authority model
Payment providers are adapters, not financial authorities. A provider may report a payment event, but authoritative state changes occur only through validated, tenant-scoped commands.

## Lifecycle
`pending -> processing -> authorized -> captured -> settled`

Terminal/error states: `failed`, `cancelled`, `refunded`.

## Capture
A payment can be captured only after a provider payment identifier exists and the internal state is `authorized` or `processing`. Capture posts:

- Debit `payment_clearing`
- Credit `accounts_receivable`

inside the same database transaction.

## Settlement
A settlement requires exact amount and currency equality with the captured payment. It posts:

- Debit `cash`
- Credit `payment_clearing`

inside the same transaction.

## Webhooks
Webhook events are tenant-scoped and idempotent by `(tenant, provider, event_id)`. Replays return the already recorded event and do not apply the transition twice.

## Reconciliation
Provider reports are classified as:
- `matched`
- `amount_mismatch`
- `currency_mismatch`
- `unknown`

Reconciliation records are immutable operational evidence; they do not silently alter authoritative finance.

## Production gates still open
- Live provider credentials and staging webhooks.
- Cryptographic verification of each provider's webhook signature.
- Live PostgreSQL integration and concurrent webhook/capture/settlement tests.
- Provider-specific adapters for Yemeni wallets/banks.
