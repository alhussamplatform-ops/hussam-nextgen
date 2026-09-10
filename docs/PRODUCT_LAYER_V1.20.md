# Product Layer v1.20

v1.20 does not add a new business engine. It adds a small read/query surface over the existing engines so a real product UI can consume operational data without reaching into persistence directly.

## Read surfaces

- Products / inventory items
- Warehouses
- Inventory movements
- Sales orders
- Suppliers
- Purchase orders
- Payment intents
- Shipments
- Finance journals
- Business documents

All reads require the existing authentication and active tenant membership boundary and are tenant-scoped at the query layer.

## Deliberate limits

This is not a full CRM, customer engine, search platform, analytics warehouse, or marketplace. Pagination is simple limit/offset (maximum 100). No schema migration is introduced.

## Next validation

The next work should exercise these read surfaces from the console/browser and then fix only issues found in the real journey. No new engine should be introduced unless a concrete business requirement proves it necessary.
