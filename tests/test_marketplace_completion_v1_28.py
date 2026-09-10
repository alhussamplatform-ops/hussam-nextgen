from decimal import Decimal
import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from app.core.persistence import Base
from app.core.models import Tenant, User, TenantMembership
from app.core.models.marketplace import MarketplaceSellerVerification, MarketplaceShippingQuote, MarketplaceFavorite, MarketplaceReturnRequest
from app.engines.identity import IdentityService
from app.engines.inventory.production import InventoryProductionService
from app.core.contracts import StockMovement
from app.engines.marketplace import MarketplaceService, ListingInput, MarketplaceError

def setup():
    e=create_engine('sqlite+pysqlite:///:memory:',future=True); Base.metadata.create_all(e); db=sessionmaker(e,expire_on_commit=False)()
    ids=IdentityService(db); seller=ids.create_tenant('Seller'); buyer_t=ids.create_tenant('Buyer'); buyer=ids.create_user('buyer','buyer@example.com'); su=ids.create_user('seller','seller@example.com'); ids.add_membership(buyer.id,buyer_t.id,'owner'); ids.add_membership(su.id,seller.id,'owner')
    inv=InventoryProductionService(db); inv.create_item(seller.id,'rice','Rice','bag'); inv.create_warehouse(seller.id,'wh','Main'); inv.record(seller.id,StockMovement('rice','wh',Decimal('20'),'in','opening'))
    m=MarketplaceService(db); m.register_seller(seller.id,'seller','Seller'); m.review_seller_verification(seller.id,su.id,'approved')
    l=m.create_listing(seller.id,ListingInput('rice','Rice','product','product','YER',Decimal('1000'),'rice','wh'))
    m.moderate_listing(l.id,su.id,'approved')
    m.publish_listing(seller.id,l.id); m.ensure_buyer(buyer.id); a=m.add_address(buyer.id,'home','Buyer','777','Aden','Aden','Street')
    return db,seller,buyer,su,l,a,m

def test_verification_is_required_for_activation_and_public_visibility():
    db,seller,buyer,su,l,a,m=setup()
    assert db.scalar(select(MarketplaceSellerVerification).where(MarketplaceSellerVerification.seller_tenant_id==seller.id)).status=='approved'
    assert m.public_listings()[0]['seller']['tenant_id']==seller.id

def test_shipping_quote_is_server_owned_and_consumed():
    db,seller,buyer,su,l,a,m=setup(); m.add_shipping_rate(seller.id,'Aden','Aden','YER',Decimal('250'))
    m.add_to_cart(buyer.id,l.id,1); q=m.quote_shipping(buyer.id,a.id,seller.id,'YER'); assert q.fee==Decimal('250.0000')
    orders=m.checkout(buyer.id,a.id,Decimal('0'),500,q.id); assert orders[0].shipping_fee==Decimal('250.0000'); assert q.consumed_at is not None
    m.add_to_cart(buyer.id,l.id,1)
    with pytest.raises(MarketplaceError): m.checkout(buyer.id,a.id,Decimal('250'),500,q.id)

def test_client_cannot_supply_arbitrary_shipping_fee():
    db,seller,buyer,su,l,a,m=setup(); m.add_to_cart(buyer.id,l.id,1)
    with pytest.raises(MarketplaceError): m.checkout(buyer.id,a.id,Decimal('10'),500)

def test_payment_intent_is_attached_to_marketplace_order():
    db,seller,buyer,su,l,a,m=setup(); m.add_to_cart(buyer.id,l.id,1); o=m.checkout(buyer.id,a.id)[0]
    p=m.attach_payment_intent(buyer.id,o.id,'provider-x'); assert o.payment_reference==p.reference
    assert p.reference.startswith('MKT-PAY:')

def test_paid_order_cannot_be_directly_cancelled():
    db,seller,buyer,su,l,a,m=setup(); m.add_to_cart(buyer.id,l.id,1); o=m.checkout(buyer.id,a.id)[0]; o.status='paid'; db.commit()
    with pytest.raises(MarketplaceError): m.cancel(buyer.id,o.id)

def test_favorite_and_return_request_are_buyer_scoped():
    db,seller,buyer,su,l,a,m=setup(); f=m.add_favorite(buyer.id,l.id); assert f.listing_id==l.id; m.remove_favorite(buyer.id,l.id); assert db.scalar(select(MarketplaceFavorite).where(MarketplaceFavorite.buyer_user_id==buyer.id)) is None
    m.add_to_cart(buyer.id,l.id,1); o=m.checkout(buyer.id,a.id)[0]; o.status='completed'; db.commit(); r=m.request_return(buyer.id,o.id,'damaged','damaged item'); assert r.status=='requested'
