from decimal import Decimal
from datetime import date
from fastapi import APIRouter, Depends, Header, Query, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import desc, select, func
from app.api.dependencies import get_context, get_session
from app.core.models.marketplace import MarketplaceSellerProfile, MarketplaceCategory, MarketplaceListing, MarketplaceOrder, MarketplaceOrderLine, MarketplacePayout, MarketplaceReview, MarketplaceDispute, MarketplaceAddress, MarketplaceSellerVerification
from app.core.models.payments import PaymentIntent
from app.engines.marketplace import MarketplaceService, ListingInput
from app.engines.payments import PaymentProductionService

router=APIRouter(prefix='/marketplace',tags=['marketplace'])

def seller_guard(ctx):
    if ctx.role not in {'owner','admin'}: raise HTTPException(status_code=403, detail='seller administration requires owner or admin role')

class SellerIn(BaseModel): slug:str; display_name:str; description:str=''; seller_type:str='business'
class CategoryIn(BaseModel): slug:str; name:str; parent_id:int|None=None
class ListingIn(BaseModel):
    slug:str; title:str; description:str=''; listing_type:str='product'; currency:str; unit_price:Decimal=Field(ge=0)
    item_id:str|None=None; warehouse_id:str|None=None; category_id:int|None=None; stock_policy:str='managed'
class BuyerIn(BaseModel): display_name:str|None=None; phone:str|None=None
class AddressIn(BaseModel): label:str; recipient_name:str; phone:str; governorate:str; city:str; address_line:str; landmark:str|None=None
class CartIn(BaseModel): listing_id:int; quantity:Decimal=Field(gt=0)
class CheckoutIn(BaseModel): shipping_address_id:int|None=None; shipping_fee:Decimal=Field(default=Decimal('0'),ge=0); shipping_quote_id:int|None=None; platform_fee_bps:int=Field(default=500,ge=0,le=3000)
class ReviewIn(BaseModel): listing_id:int; rating:int=Field(ge=1,le=5); title:str=''; body:str=''
class DisputeIn(BaseModel): reason:str; description:str
class PaymentIn(BaseModel): provider:str=Field(min_length=1,max_length=80)
class PayoutIn(BaseModel): external_reference:str=Field(min_length=1,max_length=255)

@router.get('/listings')
def public_listings(q:str|None=None,category_id:int|None=None,seller_slug:str|None=None,limit:int=Query(50,ge=1,le=100),offset:int=Query(0,ge=0),db=Depends(get_session)):
    return {'items':MarketplaceService(db).public_listings(q=q,category_id=category_id,seller_slug=seller_slug,limit=limit,offset=offset),'limit':limit,'offset':offset}

@router.get('/categories')
def categories(db=Depends(get_session)):
    rows=db.scalars(select(MarketplaceCategory).where(MarketplaceCategory.active.is_(True)).order_by(MarketplaceCategory.name)).all()
    return {'items':[{'id':x.id,'slug':x.slug,'name':x.name,'parent_id':x.parent_id} for x in rows]}

@router.get('/sellers')
def sellers(limit:int=Query(50,ge=1,le=100),offset:int=Query(0,ge=0),db=Depends(get_session)):
    rows=db.scalars(select(MarketplaceSellerProfile).join(MarketplaceSellerVerification,MarketplaceSellerVerification.seller_tenant_id==MarketplaceSellerProfile.tenant_id).where(MarketplaceSellerProfile.status=='active',MarketplaceSellerVerification.status=='approved').order_by(desc(MarketplaceSellerProfile.created_at)).limit(limit).offset(offset)).all()
    return {'items':[{'tenant_id':x.tenant_id,'slug':x.slug,'display_name':x.display_name,'description':x.description,'seller_type':x.seller_type} for x in rows]}

@router.post('/seller',status_code=201)
def register_seller(body:SellerIn,ctx=Depends(get_context),db=Depends(get_session)):
    seller_guard(ctx); x=MarketplaceService(db).register_seller(ctx.tenant_id,**body.model_dump())
    return {'tenant_id':x.tenant_id,'slug':x.slug,'display_name':x.display_name,'status':x.status}

@router.post('/seller/activate')
def activate_seller(ctx=Depends(get_context),db=Depends(get_session)):
    seller_guard(ctx); x=MarketplaceService(db).activate_seller(ctx.tenant_id); return {'tenant_id':x.tenant_id,'status':x.status}

@router.post('/categories',status_code=201)
def create_category(body:CategoryIn,ctx=Depends(get_context),db=Depends(get_session)):
    platform_admin_guard(ctx); x=MarketplaceService(db).create_category(ctx.tenant_id,**body.model_dump()); return {'id':x.id,'slug':x.slug,'name':x.name,'parent_id':x.parent_id}

@router.post('/seller/listings',status_code=201)
def create_listing(body:ListingIn,ctx=Depends(get_context),db=Depends(get_session)):
    seller_guard(ctx); x=MarketplaceService(db).create_listing(ctx.tenant_id,ListingInput(**body.model_dump())); return {'id':x.id,'slug':x.slug,'title':x.title,'status':x.status,'currency':x.currency,'unit_price':str(x.unit_price)}

@router.post('/seller/listings/{listing_id}/publish')
def publish_listing(listing_id:int,ctx=Depends(get_context),db=Depends(get_session)):
    seller_guard(ctx); x=MarketplaceService(db).publish_listing(ctx.tenant_id,listing_id); return {'id':x.id,'status':x.status}

@router.post('/seller/listings/{listing_id}/pause')
def pause_listing(listing_id:int,ctx=Depends(get_context),db=Depends(get_session)):
    seller_guard(ctx); x=MarketplaceService(db).pause_listing(ctx.tenant_id,listing_id); return {'id':x.id,'status':x.status}

@router.get('/seller/listings')
def seller_listings(ctx=Depends(get_context),db=Depends(get_session)):
    seller_guard(ctx); rows=db.scalars(select(MarketplaceListing).where(MarketplaceListing.seller_tenant_id==ctx.tenant_id).order_by(desc(MarketplaceListing.id))).all(); return {'items':[{'id':x.id,'slug':x.slug,'title':x.title,'type':x.listing_type,'status':x.status,'currency':x.currency,'unit_price':str(x.unit_price),'item_id':x.item_id,'warehouse_id':x.warehouse_id} for x in rows]}

@router.post('/buyer/profile')
def buyer_profile(body:BuyerIn,ctx=Depends(get_context),db=Depends(get_session)):
    x=MarketplaceService(db).ensure_buyer(ctx.user_id,body.display_name,body.phone); return {'user_id':x.user_id,'display_name':x.display_name,'phone':x.phone}

@router.post('/buyer/addresses',status_code=201)
def add_address(body:AddressIn,ctx=Depends(get_context),db=Depends(get_session)):
    x=MarketplaceService(db).add_address(ctx.user_id,**body.model_dump()); return {'id':x.id,'label':x.label,'recipient_name':x.recipient_name,'phone':x.phone,'governorate':x.governorate,'city':x.city,'address_line':x.address_line,'landmark':x.landmark}

@router.get('/buyer/addresses')
def addresses(ctx=Depends(get_context),db=Depends(get_session)):
    rows=db.scalars(select(MarketplaceAddress).where(MarketplaceAddress.user_id==ctx.user_id,MarketplaceAddress.active.is_(True)).order_by(desc(MarketplaceAddress.id))).all(); return {'items':[{'id':x.id,'label':x.label,'recipient_name':x.recipient_name,'phone':x.phone,'governorate':x.governorate,'city':x.city,'address_line':x.address_line,'landmark':x.landmark} for x in rows]}

@router.get('/buyer/cart')
def get_cart(ctx=Depends(get_context),db=Depends(get_session)): return MarketplaceService(db).cart_view(ctx.user_id)

@router.post('/buyer/cart/items')
def add_cart(body:CartIn,ctx=Depends(get_context),db=Depends(get_session)): MarketplaceService(db).add_to_cart(ctx.user_id,body.listing_id,body.quantity); return MarketplaceService(db).cart_view(ctx.user_id)

@router.delete('/buyer/cart/items/{listing_id}')
def remove_cart(listing_id:int,ctx=Depends(get_context),db=Depends(get_session)): MarketplaceService(db).remove_from_cart(ctx.user_id,listing_id); return MarketplaceService(db).cart_view(ctx.user_id)

@router.post('/buyer/checkout',status_code=201)
def checkout(body:CheckoutIn, idempotency_key: str | None = Header(default=None, alias='Idempotency-Key'), ctx=Depends(get_context),db=Depends(get_session)):
    orders=MarketplaceService(db).checkout(ctx.user_id,body.shipping_address_id,body.shipping_fee,body.platform_fee_bps,body.shipping_quote_id,idempotency_key,ctx.tenant_id)
    return {'orders':[{'id':o.id,'reference':o.reference,'seller_tenant_id':o.seller_tenant_id,'currency':o.currency,'subtotal':str(o.subtotal),'shipping_fee':str(o.shipping_fee),'platform_fee':str(o.platform_fee),'total':str(o.total),'status':o.status} for o in orders]}

@router.post('/buyer/orders/{order_id}/payment-intent',status_code=201)
def create_payment(order_id:int,body:PaymentIn,ctx=Depends(get_context),db=Depends(get_session)):
    p=MarketplaceService(db).attach_payment_intent(ctx.user_id,order_id,body.provider)
    return {'reference':p.reference,'provider':p.provider,'amount':str(p.amount),'currency':p.currency,'status':p.status}

@router.get('/buyer/orders')
def buyer_orders(ctx=Depends(get_context),db=Depends(get_session)):
    rows=db.scalars(select(MarketplaceOrder).where(MarketplaceOrder.buyer_user_id==ctx.user_id).order_by(desc(MarketplaceOrder.id))).all(); return {'items':[{'id':x.id,'reference':x.reference,'seller_tenant_id':x.seller_tenant_id,'currency':x.currency,'subtotal':str(x.subtotal),'shipping_fee':str(x.shipping_fee),'platform_fee':str(x.platform_fee),'total':str(x.total),'status':x.status,'payment_reference':x.payment_reference} for x in rows]}

@router.post('/buyer/orders/{order_id}/cancel')
def cancel_order(order_id:int,ctx=Depends(get_context),db=Depends(get_session)):
    x=MarketplaceService(db).cancel(ctx.user_id,order_id); return {'id':x.id,'status':x.status}

@router.post('/seller/orders/{order_id}/paid')
def mark_paid(order_id:int,payment_reference:str,ctx=Depends(get_context),db=Depends(get_session)):
    seller_guard(ctx); x=MarketplaceService(db).mark_paid(ctx.tenant_id,order_id,payment_reference); return {'id':x.id,'status':x.status,'payment_reference':x.payment_reference}

@router.post('/seller/orders/{order_id}/processing')
def processing(order_id:int,ctx=Depends(get_context),db=Depends(get_session)):
    seller_guard(ctx); x=MarketplaceService(db).mark_processing(ctx.tenant_id,order_id); return {'id':x.id,'status':x.status}

@router.post('/seller/orders/{order_id}/shipped')
def shipped(order_id:int,shipment_id:int,ctx=Depends(get_context),db=Depends(get_session)):
    seller_guard(ctx); x=MarketplaceService(db).mark_shipped(ctx.tenant_id,order_id,shipment_id); return {'id':x.id,'status':x.status}

@router.post('/seller/orders/{order_id}/delivered')
def delivered(order_id:int,shipment_id:int,ctx=Depends(get_context),db=Depends(get_session)):
    seller_guard(ctx); x=MarketplaceService(db).mark_delivered(ctx.tenant_id,order_id,shipment_id); return {'id':x.id,'status':x.status}

@router.get('/seller/orders')
def seller_orders(ctx=Depends(get_context),db=Depends(get_session)):
    seller_guard(ctx); rows=db.scalars(select(MarketplaceOrder).where(MarketplaceOrder.seller_tenant_id==ctx.tenant_id).order_by(desc(MarketplaceOrder.id))).all(); return {'items':[{'id':x.id,'reference':x.reference,'buyer_user_id':x.buyer_user_id,'total':str(x.total),'currency':x.currency,'status':x.status} for x in rows]}

@router.post('/seller/orders/{order_id}/payout-paid')
def payout_paid(order_id:int,body:PayoutIn,ctx=Depends(get_context),db=Depends(get_session)):
    seller_guard(ctx); x=MarketplaceService(db).mark_payout_paid(ctx.tenant_id,order_id,body.external_reference); return {'id':x.id,'status':x.status,'net_amount':str(x.net_amount),'currency':x.currency}

@router.get('/seller/payouts')
def seller_payouts(ctx=Depends(get_context),db=Depends(get_session)):
    seller_guard(ctx); rows=db.scalars(select(MarketplacePayout).where(MarketplacePayout.seller_tenant_id==ctx.tenant_id).order_by(desc(MarketplacePayout.id))).all(); return {'items':[{'id':x.id,'order_id':x.marketplace_order_id,'reference':x.reference,'gross_amount':str(x.gross_amount),'platform_fee':str(x.platform_fee),'net_amount':str(x.net_amount),'currency':x.currency,'status':x.status,'eligible_at':x.eligible_at.isoformat() if x.eligible_at else None,'paid_at':x.paid_at.isoformat() if x.paid_at else None} for x in rows]}

@router.post('/buyer/reviews',status_code=201)
def review(body:ReviewIn,order_id:int,ctx=Depends(get_context),db=Depends(get_session)):
    x=MarketplaceService(db).create_review(ctx.user_id,order_id,body.listing_id,body.rating,body.title,body.body); return {'id':x.id,'rating':x.rating,'status':x.status}

@router.post('/buyer/disputes',status_code=201)
def dispute(body:DisputeIn,order_id:int,ctx=Depends(get_context),db=Depends(get_session)):
    x=MarketplaceService(db).open_dispute(ctx.user_id,order_id,body.reason,body.description); return {'id':x.id,'order_id':x.marketplace_order_id,'status':x.status}

@router.get('/listings/{listing_id}')
def listing(listing_id:int,db=Depends(get_session)): return MarketplaceService(db)._listing_view(MarketplaceService(db)._listing(listing_id))

class ShippingRateIn(BaseModel):
    governorate:str; city:str|None=None; currency:str; fee:Decimal=Field(ge=0)
class ShippingQuoteIn(BaseModel):
    address_id:int; seller_tenant_id:int; currency:str
class ReturnIn(BaseModel):
    reason:str; description:str

@router.post('/seller/verification')
def submit_verification(body:dict|None=None,ctx=Depends(get_context),db=Depends(get_session)):
    seller_guard(ctx); x=MarketplaceService(db).submit_seller_verification(ctx.tenant_id,(body or {}).get('notes','')); return {'id':x.id,'status':x.status}

@router.post('/seller/shipping-rates',status_code=201)
def add_shipping_rate(body:ShippingRateIn,ctx=Depends(get_context),db=Depends(get_session)):
    seller_guard(ctx); x=MarketplaceService(db).add_shipping_rate(ctx.tenant_id,**body.model_dump()); return {'id':x.id,'governorate':x.governorate,'city':x.city,'currency':x.currency,'fee':str(x.fee)}

@router.post('/buyer/shipping-quotes',status_code=201)
def shipping_quote(body:ShippingQuoteIn,ctx=Depends(get_context),db=Depends(get_session)):
    x=MarketplaceService(db).quote_shipping(ctx.user_id,body.address_id,body.seller_tenant_id,body.currency); return {'id':x.id,'seller_tenant_id':x.seller_tenant_id,'address_id':x.address_id,'currency':x.currency,'fee':str(x.fee),'expires_at':x.expires_at.isoformat()}

@router.post('/buyer/favorites/{listing_id}',status_code=201)
def favorite(listing_id:int,ctx=Depends(get_context),db=Depends(get_session)):
    x=MarketplaceService(db).add_favorite(ctx.user_id,listing_id); return {'id':x.id,'listing_id':x.listing_id}

@router.delete('/buyer/favorites/{listing_id}')
def unfavorite(listing_id:int,ctx=Depends(get_context),db=Depends(get_session)):
    MarketplaceService(db).remove_favorite(ctx.user_id,listing_id); return {'status':'removed'}

@router.post('/buyer/orders/{order_id}/sync-payment')
def sync_payment(order_id:int,ctx=Depends(get_context),db=Depends(get_session)):
    x=MarketplaceService(db).sync_payment(ctx.user_id,order_id); return {'id':x.id,'status':x.status,'payment_reference':x.payment_reference}

@router.post('/buyer/orders/{order_id}/returns',status_code=201)
def request_return(order_id:int,body:ReturnIn,ctx=Depends(get_context),db=Depends(get_session)):
    x=MarketplaceService(db).request_return(ctx.user_id,order_id,body.reason,body.description); return {'id':x.id,'order_id':x.marketplace_order_id,'status':x.status}


class VerificationReviewIn(BaseModel):
    seller_tenant_id:int; decision:str; notes:str=''

@router.post('/platform/seller-verifications/review')
def review_verification(body:VerificationReviewIn,ctx=Depends(get_context),db=Depends(get_session)):
    if ctx.role != 'platform_admin': raise HTTPException(status_code=403, detail='platform operator role required')
    x=MarketplaceService(db).review_seller_verification(body.seller_tenant_id,ctx.user_id,body.decision,body.notes)
    return {'id':x.id,'seller_tenant_id':x.seller_tenant_id,'status':x.status,'reviewed_at':x.reviewed_at.isoformat() if x.reviewed_at else None}

class ModerationIn(BaseModel):
    listing_id:int; decision:str; notes:str=''
class PayoutDestinationIn(BaseModel):
    provider:str=Field(min_length=1,max_length=80); external_reference:str=Field(min_length=1,max_length=255)


def platform_admin_guard(ctx):
    if ctx.role != 'platform_admin':
        raise HTTPException(status_code=403, detail='platform administrator role required')

@router.get('/seller/status')
def seller_status(ctx=Depends(get_context),db=Depends(get_session)):
    seller= db.scalar(select(MarketplaceSellerProfile).where(MarketplaceSellerProfile.tenant_id==ctx.tenant_id))
    verification=db.scalar(select(MarketplaceSellerVerification).where(MarketplaceSellerVerification.seller_tenant_id==ctx.tenant_id))
    if not seller: return {'registered':False}
    return {'registered':True,'tenant_id':seller.tenant_id,'slug':seller.slug,'status':seller.status,'verification':verification.status if verification else None}

@router.get('/seller/payout-destination')
def payout_destination(ctx=Depends(get_context),db=Depends(get_session)):
    seller_guard(ctx)
    from app.core.models.marketplace import MarketplacePayoutDestination
    x=db.scalar(select(MarketplacePayoutDestination).where(MarketplacePayoutDestination.seller_tenant_id==ctx.tenant_id))
    return {'destination':None if not x else {'provider':x.provider,'external_reference':x.external_reference,'status':x.status,'verified_at':x.verified_at.isoformat() if x.verified_at else None}}

@router.post('/seller/payout-destination',status_code=201)
def set_payout_destination(body:PayoutDestinationIn,ctx=Depends(get_context),db=Depends(get_session)):
    seller_guard(ctx)
    x=MarketplaceService(db).set_payout_destination(ctx.tenant_id,body.provider,body.external_reference)
    return {'seller_tenant_id':x.seller_tenant_id,'provider':x.provider,'external_reference':x.external_reference,'status':x.status}

@router.post('/platform/payout-destinations/{seller_tenant_id}/verify')
def verify_payout_destination(seller_tenant_id:int,ctx=Depends(get_context),db=Depends(get_session)):
    platform_admin_guard(ctx)
    x=MarketplaceService(db).verify_payout_destination(seller_tenant_id,ctx.user_id)
    return {'seller_tenant_id':x.seller_tenant_id,'status':x.status,'verified_at':x.verified_at.isoformat() if x.verified_at else None}

@router.post('/platform/listings/moderate')
def moderate_listing(body:ModerationIn,ctx=Depends(get_context),db=Depends(get_session)):
    platform_admin_guard(ctx)
    x=MarketplaceService(db).moderate_listing(body.listing_id,ctx.user_id,body.decision,body.notes)
    return {'id':x.id,'seller_tenant_id':x.seller_tenant_id,'status':x.status,'moderation_status':x.moderation_status}

@router.get('/platform/listings/pending-moderation')
def pending_moderation(ctx=Depends(get_context),db=Depends(get_session)):
    platform_admin_guard(ctx)
    rows=db.scalars(select(MarketplaceListing).where(MarketplaceListing.moderation_status=='pending').order_by(desc(MarketplaceListing.id)).limit(100)).all()
    return {'items':[{'id':x.id,'seller_tenant_id':x.seller_tenant_id,'slug':x.slug,'title':x.title,'status':x.status,'moderation_status':x.moderation_status} for x in rows]}

@router.get('/platform/categories')
def platform_categories(ctx=Depends(get_context),db=Depends(get_session)):
    platform_admin_guard(ctx)
    rows=db.scalars(select(MarketplaceCategory).order_by(MarketplaceCategory.id)).all()
    return {'items':[{'id':x.id,'slug':x.slug,'name':x.name,'parent_id':x.parent_id,'active':x.active} for x in rows]}
