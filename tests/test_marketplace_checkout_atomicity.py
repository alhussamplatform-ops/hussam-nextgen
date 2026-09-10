from decimal import Decimal

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from app.core.contracts import StockMovement
from app.core.models import Base, Tenant, User, TenantMembership
from app.core.models.commerce import SalesOrder
from app.core.models.inventory import InventoryReservation
from app.core.models.marketplace import MarketplaceCart, MarketplaceOrder, MarketplacePayout
from app.engines.identity import IdentityService
from app.engines.inventory.production import InventoryProductionService
from app.engines.commerce import CommerceProductionService
from app.engines.marketplace import ListingInput, MarketplaceError, MarketplaceService


def setup():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    db = sessionmaker(engine, expire_on_commit=False)()
    identities = IdentityService(db)
    seller = identities.create_tenant("Seller")
    buyer_tenant = identities.create_tenant("Buyer")
    buyer = identities.create_user("buyer", "buyer@example.com")
    seller_user = identities.create_user("seller", "seller@example.com")
    identities.add_membership(buyer.id, buyer_tenant.id, "owner")
    identities.add_membership(seller_user.id, seller.id, "owner")
    inventory = InventoryProductionService(db)
    inventory.create_item(seller.id, "item", "Item")
    inventory.create_warehouse(seller.id, "warehouse", "Warehouse")
    inventory.record(seller.id, StockMovement("item", "warehouse", Decimal("10"), "in", "opening"))
    marketplace = MarketplaceService(db)
    marketplace.register_seller(seller.id, "seller", "Seller")
    marketplace.review_seller_verification(seller.id, seller_user.id, "approved")
    listing = marketplace.create_listing(
        seller.id,
        ListingInput("item", "Item", "", "product", "YER", Decimal("10"), "item", "warehouse"),
    )
    marketplace.moderate_listing(listing.id, seller_user.id, "approved")
    marketplace.publish_listing(seller.id, listing.id)
    marketplace.ensure_buyer(buyer.id)
    return db, seller, buyer_tenant, buyer, listing


def test_checkout_is_idempotent_and_tenant_bound():
    db, _, buyer_tenant, buyer, listing = setup()
    service = MarketplaceService(db)
    service.add_to_cart(buyer.id, listing.id, 2)

    first = service.checkout(buyer.id, idempotency_key="checkout-1", tenant_id=buyer_tenant.id)
    second = service.checkout(buyer.id, idempotency_key="checkout-1", tenant_id=buyer_tenant.id)

    assert [order.id for order in second] == [order.id for order in first]
    assert db.query(MarketplaceOrder).count() == 1
    assert db.query(SalesOrder).count() == 1
    assert db.query(MarketplacePayout).count() == 1

    with pytest.raises(MarketplaceError, match="different checkout"):
        service.checkout(buyer.id, shipping_fee=Decimal("1"), idempotency_key="checkout-1", tenant_id=buyer_tenant.id)


def test_checkout_rolls_back_sales_order_and_reservation_on_failure(monkeypatch):
    db, _, buyer_tenant, buyer, listing = setup()
    service = MarketplaceService(db)
    service.add_to_cart(buyer.id, listing.id, 2)

    def fail_after_marketplace_order(*args, **kwargs):
        raise MarketplaceError("injected checkout failure")

    monkeypatch.setattr(service, "_event", fail_after_marketplace_order)
    with pytest.raises(MarketplaceError, match="injected checkout failure"):
        service.checkout(buyer.id, idempotency_key="checkout-failure", tenant_id=buyer_tenant.id)

    assert db.query(SalesOrder).count() == 0
    assert db.query(InventoryReservation).count() == 0
    assert db.query(MarketplaceOrder).count() == 0
    assert db.query(MarketplacePayout).count() == 0


@pytest.mark.parametrize("failure_stage", ["before_commerce", "after_sales_order", "marketplace_order", "payout"])
def test_checkout_failure_stages_are_atomic(monkeypatch, failure_stage):
    db, _, buyer_tenant, buyer, listing = setup()
    service = MarketplaceService(db)
    service.add_to_cart(buyer.id, listing.id, 2)

    if failure_stage == "before_commerce":
        def fail_before(*args, **kwargs):
            raise MarketplaceError("before commerce")
        monkeypatch.setattr(CommerceProductionService, "create_draft", fail_before)
    elif failure_stage == "after_sales_order":
        original_create = CommerceProductionService.create_draft
        def fail_after(service_instance, *args, **kwargs):
            original_create(service_instance, *args, **kwargs)
            raise MarketplaceError("after sales order")
        monkeypatch.setattr(CommerceProductionService, "create_draft", fail_after)
    else:
        original_add = db.add
        target = MarketplaceOrder if failure_stage == "marketplace_order" else MarketplacePayout
        def fail_during_add(value, _warn=True):
            if isinstance(value, target):
                raise MarketplaceError(failure_stage)
            return original_add(value, _warn)
        monkeypatch.setattr(db, "add", fail_during_add)

    with pytest.raises(MarketplaceError):
        service.checkout(buyer.id, idempotency_key=f"failure-{failure_stage}", tenant_id=buyer_tenant.id)

    assert db.query(SalesOrder).count() == 0
    assert db.query(InventoryReservation).count() == 0
    assert db.query(MarketplaceOrder).count() == 0
    assert db.query(MarketplacePayout).count() == 0


def test_checkout_rejects_inactive_or_empty_cart():
    db, _, buyer_tenant, buyer, listing = setup()
    service = MarketplaceService(db)
    cart = service.cart(buyer.id)
    cart.status = "checked_out"
    db.commit()

    with pytest.raises(MarketplaceError, match="not active"):
        service.checkout(buyer.id, idempotency_key="inactive-cart", tenant_id=buyer_tenant.id)

    cart.status = "active"
    db.commit()
    with pytest.raises(MarketplaceError, match="empty"):
        service.checkout(buyer.id, idempotency_key="empty-cart", tenant_id=buyer_tenant.id)
