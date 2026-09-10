# Marketplace v1.27

## Purpose
Hussam Marketplace is a multi-seller commerce layer above the sovereign platform. It supports B2C, B2B and C2C/B2B2C participation without making Marketplace the source of truth for stock, payments, logistics or accounting.

## Core capabilities
1. Seller registration, activation and suspension-ready lifecycle.
2. Public catalog of published listings from active sellers.
3. Product listings linked to seller inventory item + warehouse.
4. Service listings that do not require inventory.
5. Categories and seller profiles.
6. Buyer profile and structured address model including governorate/city/landmark.
7. One active cart per buyer with multiple sellers.
8. Checkout splits a multi-seller cart into one marketplace order per seller/currency.
9. Product orders create and confirm authoritative Commerce orders, which create Inventory reservations.
10. Platform commission is seller-funded; buyer total excludes the seller commission.
11. Provider-agnostic payment intent creation through the existing Payments Engine.
12. Paid/processing/shipped/delivered/completed lifecycle.
13. Seller payout held → eligible → paid facts.
14. Buyer reviews after completed orders.
15. Buyer disputes with explicit order linkage.
16. Outbox events for marketplace lifecycle events.

## Order and money boundary
Marketplace records commercial intent and allocation facts. It does not post arbitrary accounting journals or mutate provider payment state directly. Payment must be captured by the Payments Engine before a marketplace order is marked paid. Inventory reservation and fulfillment remain owned by the Inventory/Commerce engines.

## Multi-seller behavior
A single buyer cart may contain listings from multiple sellers. Checkout groups lines by seller and currency. Each group becomes an independent marketplace order and, for physical products, an independent seller-side SalesOrder. This keeps seller inventory, payment and fulfillment boundaries explicit.

## Catalog visibility
Only `published` listings belonging to an `active` seller appear in public catalog endpoints. Seller management operations are authenticated and seller-tenant scoped.

## Services
Service listings are first-class catalog objects and do not require inventory references. Physical fulfillment remains a product-specific flow. Future service booking/scheduling can use the same listing/order contract without introducing a second marketplace.

## Refunds, disputes and risk
The current core records disputes and preserves payout hold state. Provider-specific refunds/chargebacks are intentionally delegated to the Payments Engine and real provider adapter. Marketplace must never infer a successful refund from a client request.

## Media
No object-storage engine was added. Listing media should use the existing Documents/business-record layer plus a future object-storage adapter. This avoids coupling Marketplace to a storage vendor.

## Security model
The design explicitly addresses object-level and function-level authorization because OWASP identifies Broken Object Level Authorization and Broken Function Level Authorization as major API risks. Every buyer/seller mutation checks the authenticated owner of the relevant object or seller tenant.

## Future extension points
- listing media and variants
- promotions/coupons
- shipping rate engine
- returns/refunds workflow
- moderation and trust/safety
- seller verification/KYC adapters
- fraud/risk scoring
- notifications
- search indexing
- service scheduling
These should extend Marketplace through contracts rather than bypassing Core.
