from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
from decimal import Decimal, ROUND_HALF_UP
import hashlib
import json
from uuid import uuid4
from sqlalchemy import select, func, or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.models.core import User, Tenant
from app.core.models.core import IdempotencyRecord
from app.core.governance.idempotency import IdempotencyResult, ensure_same_request, IdempotencyConflict
from app.core.models.marketplace import (
    MarketplaceSellerProfile, MarketplaceCategory, MarketplaceListing,
    MarketplaceBuyerProfile, MarketplaceAddress, MarketplaceCart, MarketplaceCartItem,
    MarketplaceOrder, MarketplaceOrderLine, MarketplacePayout, MarketplaceReview, MarketplaceDispute,
    MarketplaceSellerVerification, MarketplaceShippingRate, MarketplaceShippingQuote, MarketplaceFavorite, MarketplaceReturnRequest, MarketplacePayoutDestination,
)
from app.core.models.payments import PaymentIntent
from app.core.models.logistics import Shipment
from app.core.models.commerce import SalesOrder, SalesOrderLine
from app.core.models.inventory import InventoryItem, Warehouse
from app.core.models.governance import OutboxEvent
from app.engines.commerce import CommerceProductionService, OrderLineInput

class MarketplaceError(ValueError): pass

@dataclass(frozen=True)
class ListingInput:
    slug: str
    title: str
    description: str
    listing_type: str
    currency: str
    unit_price: Decimal
    item_id: str | None = None
    warehouse_id: str | None = None
    category_id: int | None = None
    stock_policy: str = 'managed'


def _money(v):
    return Decimal(str(v)).quantize(Decimal('0.0001'), rounding=ROUND_HALF_UP)

def _positive(v, label):
    x=_money(v)
    if x <= 0: raise MarketplaceError(f'{label} must be positive')
    return x

def _nonnegative(v, label):
    x=_money(v)
    if x < 0: raise MarketplaceError(f'{label} cannot be negative')
    return x

class MarketplaceService:
    """Marketplace orchestration. Catalog facts live here; finance/inventory/commerce remain authoritative."""
    def __init__(self, db: Session): self.db=db

    def _event(self, tenant_id, typ, aggregate_type, aggregate_id, payload):
        self.db.add(OutboxEvent(event_id=str(uuid4()),tenant_id=tenant_id,event_type=typ,aggregate_type=aggregate_type,aggregate_id=str(aggregate_id),payload=payload,published=False))

    def _seller(self, tenant_id, active=False):
        q=select(MarketplaceSellerProfile).where(MarketplaceSellerProfile.tenant_id==tenant_id)
        if active:
            q=q.join(MarketplaceSellerVerification,MarketplaceSellerVerification.seller_tenant_id==MarketplaceSellerProfile.tenant_id).where(MarketplaceSellerProfile.status=='active',MarketplaceSellerVerification.status=='approved')
        x=self.db.scalar(q)
        if not x: raise MarketplaceError('marketplace seller profile not found')
        return x

    def register_seller(self, tenant_id:int, slug:str, display_name:str, description:str='', seller_type:str='business'):
        if not slug or not display_name: raise MarketplaceError('seller slug and display name are required')
        tenant=self.db.scalar(select(Tenant).where(Tenant.id==tenant_id,Tenant.status=='active'))
        if not tenant: raise MarketplaceError('active tenant required')
        if self.db.scalar(select(MarketplaceSellerProfile).where(MarketplaceSellerProfile.tenant_id==tenant_id)): raise MarketplaceError('seller profile already exists')
        if self.db.scalar(select(MarketplaceSellerProfile).where(MarketplaceSellerProfile.slug==slug)): raise MarketplaceError('seller slug already exists')
        x=MarketplaceSellerProfile(tenant_id=tenant_id,slug=slug.strip(),display_name=display_name.strip(),description=description or '',seller_type=seller_type,status='pending')
        self.db.add(x); self.db.flush()
        self.db.add(MarketplaceSellerVerification(seller_tenant_id=tenant_id,status='pending'))
        self._event(tenant_id,'marketplace.seller.registered','seller',tenant_id,{'slug':x.slug}); self.db.commit(); return x

    def activate_seller(self, tenant_id:int):
        x=self._seller(tenant_id)
        verification=self.db.scalar(select(MarketplaceSellerVerification).where(MarketplaceSellerVerification.seller_tenant_id==tenant_id))
        if not verification or verification.status!='approved': raise MarketplaceError('seller verification approval is required before activation')
        if x.status not in {'pending','suspended'}: raise MarketplaceError('seller cannot be activated from current status')
        x.status='active'; self._event(tenant_id,'marketplace.seller.activated','seller',tenant_id,{}); self.db.commit(); return x

    def create_category(self, tenant_id:int, slug:str, name:str, parent_id:int|None=None):
        self._seller(tenant_id)
        if not slug or not name: raise MarketplaceError('category slug and name are required')
        if self.db.scalar(select(MarketplaceCategory).where(MarketplaceCategory.slug==slug)): raise MarketplaceError('category slug already exists')
        if parent_id and not self.db.scalar(select(MarketplaceCategory).where(MarketplaceCategory.id==parent_id,MarketplaceCategory.active.is_(True))): raise MarketplaceError('parent category not found')
        x=MarketplaceCategory(slug=slug.strip(),name=name.strip(),parent_id=parent_id,active=True); self.db.add(x); self.db.flush(); self._event(tenant_id,'marketplace.category.created','category',x.id,{'slug':x.slug}); self.db.commit(); return x

    def submit_seller_verification(self, tenant_id:int, notes:str=''):
        self._seller(tenant_id)
        x=self.db.scalar(select(MarketplaceSellerVerification).where(MarketplaceSellerVerification.seller_tenant_id==tenant_id))
        if x and x.status=='approved': raise MarketplaceError('seller is already verified')
        if not x:
            x=MarketplaceSellerVerification(seller_tenant_id=tenant_id,status='pending',notes=notes or '')
            self.db.add(x); self.db.flush()
        else:
            x.status='pending'; x.notes=notes or ''; x.submitted_at=datetime.now(timezone.utc); x.reviewed_at=None; x.reviewer_user_id=None
        self._event(tenant_id,'marketplace.seller.verification_submitted','seller_verification',x.id if x.id else tenant_id,{})
        self.db.commit(); self.db.refresh(x); return x

    def review_seller_verification(self, seller_tenant_id:int, reviewer_user_id:str, decision:str, notes:str=''):
        if decision not in {'approved','rejected'}: raise MarketplaceError('verification decision must be approved or rejected')
        x=self.db.scalar(select(MarketplaceSellerVerification).where(MarketplaceSellerVerification.seller_tenant_id==seller_tenant_id).with_for_update())
        if not x: raise MarketplaceError('verification request not found')
        x.status=decision; x.reviewed_at=datetime.now(timezone.utc); x.reviewer_user_id=reviewer_user_id; x.notes=notes or x.notes
        if decision=='approved':
            seller=self._seller(seller_tenant_id)
            if seller.status=='pending': seller.status='active'
        self._event(seller_tenant_id,'marketplace.seller.verification_'+decision,'seller_verification',x.id,{'reviewer_user_id':reviewer_user_id})
        self.db.commit(); return x

    def set_payout_destination(self, seller_tenant_id:int, provider:str, external_reference:str, status:str='pending'):
        self._seller(seller_tenant_id,active=True)
        if status not in {'pending','verified','disabled'}: raise MarketplaceError('invalid payout destination status')
        if not provider or not external_reference: raise MarketplaceError('payout destination provider and reference are required')
        x=self.db.scalar(select(MarketplacePayoutDestination).where(MarketplacePayoutDestination.seller_tenant_id==seller_tenant_id))
        if not x:
            x=MarketplacePayoutDestination(seller_tenant_id=seller_tenant_id,provider=provider.strip(),external_reference=external_reference.strip(),status='pending')
            self.db.add(x)
        else:
            x.provider=provider.strip(); x.external_reference=external_reference.strip(); x.status=status
        if status=='verified': x.verified_at=datetime.now(timezone.utc)
        self._event(seller_tenant_id,'marketplace.payout_destination.updated','payout_destination',seller_tenant_id,{'provider':x.provider,'status':x.status})
        self.db.commit(); self.db.refresh(x); return x

    def verify_payout_destination(self, seller_tenant_id:int, reviewer_user_id:str):
        x=self.db.scalar(select(MarketplacePayoutDestination).where(MarketplacePayoutDestination.seller_tenant_id==seller_tenant_id).with_for_update())
        if not x: raise MarketplaceError('payout destination not found')
        x.status='verified'; x.verified_at=datetime.now(timezone.utc)
        self._event(seller_tenant_id,'marketplace.payout_destination.verified','payout_destination',seller_tenant_id,{'reviewer_user_id':reviewer_user_id})
        self.db.commit(); return x

    def add_shipping_rate(self, seller_tenant_id:int, governorate:str, city:str|None, currency:str, fee:Decimal):
        self._seller(seller_tenant_id,active=True)
        if not governorate or not currency: raise MarketplaceError('governorate and currency are required')
        f=_nonnegative(fee,'shipping fee')
        x=MarketplaceShippingRate(seller_tenant_id=seller_tenant_id,governorate=governorate.strip(),city=city.strip() if city else None,currency=currency.strip().upper(),fee=f,active=True)
        self.db.add(x); self.db.flush(); self._event(seller_tenant_id,'marketplace.shipping_rate.created','shipping_rate',x.id,{'fee':str(f),'currency':x.currency}); self.db.commit(); return x

    def quote_shipping(self,user_id:str,address_id:int,seller_tenant_id:int,currency:str):
        address=self.db.scalar(select(MarketplaceAddress).where(MarketplaceAddress.id==address_id,MarketplaceAddress.user_id==user_id,MarketplaceAddress.active.is_(True)))
        if not address: raise MarketplaceError('shipping address does not belong to buyer')
        q=select(MarketplaceShippingRate).where(MarketplaceShippingRate.seller_tenant_id==seller_tenant_id,MarketplaceShippingRate.governorate==address.governorate,MarketplaceShippingRate.currency==currency.upper(),MarketplaceShippingRate.active.is_(True),MarketplaceShippingRate.city==address.city)
        rate=self.db.scalar(q)
        if not rate:
            q=q.where(MarketplaceShippingRate.city.is_(None)); rate=self.db.scalar(q)
        if not rate: raise MarketplaceError('no shipping rate for destination and currency')
        quote=MarketplaceShippingQuote(buyer_user_id=user_id,seller_tenant_id=seller_tenant_id,address_id=address_id,currency=currency.upper(),fee=_money(rate.fee),expires_at=datetime.now(timezone.utc).replace(microsecond=0)+timedelta(minutes=30))
        self.db.add(quote); self.db.commit(); self.db.refresh(quote); return quote

    def add_favorite(self,user_id:str,listing_id:int):
        self.ensure_buyer(user_id); self._listing(listing_id,public=True)
        if self.db.scalar(select(MarketplaceFavorite).where(MarketplaceFavorite.buyer_user_id==user_id,MarketplaceFavorite.listing_id==listing_id)): return self.db.scalar(select(MarketplaceFavorite).where(MarketplaceFavorite.buyer_user_id==user_id,MarketplaceFavorite.listing_id==listing_id))
        x=MarketplaceFavorite(buyer_user_id=user_id,listing_id=listing_id); self.db.add(x); self.db.commit(); return x

    def remove_favorite(self,user_id:str,listing_id:int):
        x=self.db.scalar(select(MarketplaceFavorite).where(MarketplaceFavorite.buyer_user_id==user_id,MarketplaceFavorite.listing_id==listing_id))
        if x: self.db.delete(x); self.db.commit()

    def sync_payment(self,buyer_user_id:str,order_id:int):
        o=self._order(buyer_user_id,order_id,lock=True)
        if o.status!='pending_payment': return o
        p=self.db.scalar(select(PaymentIntent).where(PaymentIntent.tenant_id==o.seller_tenant_id,PaymentIntent.reference==o.payment_reference,PaymentIntent.status=='captured')) if o.payment_reference else None
        if not p: raise MarketplaceError('captured marketplace payment not found')
        if p.currency!=o.currency or _money(p.amount)!=_money(o.total): raise MarketplaceError('payment does not match order')
        o.status='paid'; o.updated_at=datetime.now(timezone.utc); self._event(o.seller_tenant_id,'marketplace.order.paid','marketplace_order',o.id,{'payment_reference':p.reference,'source':'payment_sync'}); self.db.commit(); return o

    def request_return(self,buyer_user_id:str,order_id:int,reason:str,description:str):
        o=self._order(buyer_user_id,order_id,lock=True)
        if o.status not in {'delivered','completed','disputed'}: raise MarketplaceError('return is only available after delivery')
        if self.db.scalar(select(MarketplaceReturnRequest).where(MarketplaceReturnRequest.marketplace_order_id==o.id)): raise MarketplaceError('return request already exists')
        x=MarketplaceReturnRequest(marketplace_order_id=o.id,opened_by_user_id=buyer_user_id,reason=reason,description=description,status='requested'); self.db.add(x); self._event(o.seller_tenant_id,'marketplace.return.requested','return_request',x.id if x.id else order_id,{'order_id':order_id,'reason':reason}); self.db.commit(); return x

    def create_listing(self, tenant_id:int, data:ListingInput):
        seller=self._seller(tenant_id,active=True)
        if not data.slug or not data.title or not data.currency: raise MarketplaceError('listing identity fields are required')
        if data.stock_policy not in {'managed','unmanaged'}: raise MarketplaceError('unsupported stock policy')
        if self.db.scalar(select(MarketplaceListing).where(MarketplaceListing.seller_tenant_id==tenant_id,MarketplaceListing.slug==data.slug)): raise MarketplaceError('listing slug already exists')
        if data.listing_type not in {'product','service'}: raise MarketplaceError('unsupported listing type')
        price=_nonnegative(data.unit_price,'unit price')
        if data.listing_type=='product':
            if not data.item_id or not data.warehouse_id: raise MarketplaceError('product listing requires item and warehouse')
            if not self.db.scalar(select(InventoryItem).where(InventoryItem.tenant_id==tenant_id,InventoryItem.id==data.item_id,InventoryItem.active.is_(True))): raise MarketplaceError('product item not found in seller tenant')
            if not self.db.scalar(select(Warehouse).where(Warehouse.tenant_id==tenant_id,Warehouse.id==data.warehouse_id,Warehouse.active.is_(True))): raise MarketplaceError('product warehouse not found in seller tenant')
        if data.category_id and not self.db.scalar(select(MarketplaceCategory).where(MarketplaceCategory.id==data.category_id,MarketplaceCategory.active.is_(True))): raise MarketplaceError('category not found')
        x=MarketplaceListing(seller_tenant_id=tenant_id,item_id=data.item_id,warehouse_id=data.warehouse_id,category_id=data.category_id,slug=data.slug.strip(),title=data.title.strip(),description=data.description or '',listing_type=data.listing_type,currency=data.currency.strip().upper(),unit_price=price,status='draft',stock_policy=data.stock_policy,moderation_status='pending')
        self.db.add(x); self.db.flush(); self._event(tenant_id,'marketplace.listing.created','listing',x.id,{'title':x.title,'type':x.listing_type}); self.db.commit(); self.db.refresh(x); return x

    def publish_listing(self, tenant_id:int, listing_id:int):
        x=self.db.scalar(select(MarketplaceListing).where(MarketplaceListing.id==listing_id,MarketplaceListing.seller_tenant_id==tenant_id))
        if not x: raise MarketplaceError('listing not found in seller tenant')
        self._seller(tenant_id,active=True)
        if x.status not in {'draft','paused'}: raise MarketplaceError('listing cannot be published from current status')
        if x.moderation_status!='approved': raise MarketplaceError('listing moderation approval is required before publication')
        x.status='published'; x.updated_at=datetime.now(timezone.utc); self._event(tenant_id,'marketplace.listing.published','listing',x.id,{'slug':x.slug}); self.db.commit(); return x

    def moderate_listing(self, listing_id:int, reviewer_user_id:str, decision:str, notes:str=''):
        if decision not in {'approved','rejected','suspended'}: raise MarketplaceError('listing moderation decision is invalid')
        x=self.db.scalar(select(MarketplaceListing).where(MarketplaceListing.id==listing_id).with_for_update())
        if not x: raise MarketplaceError('listing not found')
        x.moderation_status=decision
        if decision in {'rejected','suspended'} and x.status=='published': x.status='paused'
        x.updated_at=datetime.now(timezone.utc)
        self._event(x.seller_tenant_id,'marketplace.listing.moderated','listing',x.id,{'decision':decision,'reviewer_user_id':reviewer_user_id,'notes':notes or ''})
        self.db.commit(); return x

    def pause_listing(self, tenant_id:int, listing_id:int):
        x=self.db.scalar(select(MarketplaceListing).where(MarketplaceListing.id==listing_id,MarketplaceListing.seller_tenant_id==tenant_id))
        if not x: raise MarketplaceError('listing not found in seller tenant')
        if x.status!='published': raise MarketplaceError('only published listings can be paused')
        x.status='paused'; x.updated_at=datetime.now(timezone.utc); self._event(tenant_id,'marketplace.listing.paused','listing',x.id,{}); self.db.commit(); return x

    def _listing(self, listing_id, public=True):
        q=select(MarketplaceListing).where(MarketplaceListing.id==listing_id)
        if public: q=q.where(MarketplaceListing.status=='published',MarketplaceListing.moderation_status=='approved')
        x=self.db.scalar(q)
        if not x: raise MarketplaceError('published listing not found')
        return x

    def public_listings(self, *, q:str|None=None, category_id:int|None=None, seller_slug:str|None=None, limit:int=50, offset:int=0):
        limit=min(max(limit,1),100); offset=max(offset,0)
        stmt=select(MarketplaceListing,MarketplaceSellerProfile).join(MarketplaceSellerProfile,MarketplaceSellerProfile.tenant_id==MarketplaceListing.seller_tenant_id).join(MarketplaceSellerVerification,MarketplaceSellerVerification.seller_tenant_id==MarketplaceListing.seller_tenant_id).where(MarketplaceListing.status=='published',MarketplaceListing.moderation_status=='approved',MarketplaceSellerProfile.status=='active',MarketplaceSellerVerification.status=='approved')
        if q: stmt=stmt.where(or_(MarketplaceListing.title.ilike(f'%{q}%'),MarketplaceListing.description.ilike(f'%{q}%')))
        if category_id: stmt=stmt.where(MarketplaceListing.category_id==category_id)
        if seller_slug: stmt=stmt.where(MarketplaceSellerProfile.slug==seller_slug)
        rows=self.db.execute(stmt.order_by(MarketplaceListing.id.desc()).limit(limit).offset(offset)).all()
        return [self._listing_view(x,s) for x,s in rows]

    def _stock(self, listing):
        if listing.listing_type!='product' or listing.stock_policy=='unmanaged': return None
        from app.engines.inventory.production import InventoryProductionService
        try: return InventoryProductionService(self.db).snapshot(listing.seller_tenant_id,listing.item_id,listing.warehouse_id).available
        except Exception: return Decimal('0')

    def _listing_view(self,x,seller=None):
        seller=seller or self._seller(x.seller_tenant_id)
        stock=self._stock(x)
        return {'id':x.id,'slug':x.slug,'title':x.title,'description':x.description,'listing_type':x.listing_type,'currency':x.currency,'unit_price':str(x.unit_price),'stock':str(stock) if stock is not None else None,'category_id':x.category_id,'seller':{'tenant_id':seller.tenant_id,'slug':seller.slug,'display_name':seller.display_name,'seller_type':seller.seller_type},'moderation_status':x.moderation_status}

    def ensure_buyer(self,user_id,display_name=None,phone=None):
        user=self.db.scalar(select(User).where(User.id==user_id,User.active.is_(True)))
        if not user: raise MarketplaceError('active user required')
        x=self.db.scalar(select(MarketplaceBuyerProfile).where(MarketplaceBuyerProfile.user_id==user_id))
        if not x:
            x=MarketplaceBuyerProfile(user_id=user_id,display_name=(display_name or user.email).strip(),phone=phone); self.db.add(x); self.db.commit()
        return x

    def add_address(self,user_id, label, recipient_name, phone, governorate, city, address_line, landmark=None):
        self.ensure_buyer(user_id)
        if not all([label,recipient_name,phone,governorate,city,address_line]): raise MarketplaceError('complete address is required')
        x=MarketplaceAddress(user_id=user_id,label=label,recipient_name=recipient_name,phone=phone,governorate=governorate,city=city,address_line=address_line,landmark=landmark,active=True)
        self.db.add(x); self.db.commit(); return x

    def cart(self,user_id):
        self.ensure_buyer(user_id)
        x=self.db.scalar(select(MarketplaceCart).where(MarketplaceCart.buyer_user_id==user_id,MarketplaceCart.status=='active'))
        if not x:
            x=MarketplaceCart(buyer_user_id=user_id,status='active'); self.db.add(x); self.db.commit(); self.db.refresh(x)
        return x

    def add_to_cart(self,user_id,listing_id,quantity):
        q=_positive(quantity,'quantity'); cart=self.cart(user_id); listing=self._listing(listing_id,public=True)
        item=self.db.scalar(select(MarketplaceCartItem).where(MarketplaceCartItem.cart_id==cart.id,MarketplaceCartItem.listing_id==listing_id))
        if item: item.quantity=_money(item.quantity)+q
        else: self.db.add(MarketplaceCartItem(cart_id=cart.id,listing_id=listing_id,quantity=q))
        cart.updated_at=datetime.now(timezone.utc); self.db.commit(); return cart

    def remove_from_cart(self,user_id,listing_id):
        cart=self.cart(user_id); item=self.db.scalar(select(MarketplaceCartItem).where(MarketplaceCartItem.cart_id==cart.id,MarketplaceCartItem.listing_id==listing_id))
        if item: self.db.delete(item); cart.updated_at=datetime.now(timezone.utc); self.db.commit()
        return cart

    def cart_view(self,user_id):
        cart=self.cart(user_id); rows=self.db.execute(select(MarketplaceCartItem,MarketplaceListing,MarketplaceSellerProfile).join(MarketplaceListing,MarketplaceListing.id==MarketplaceCartItem.listing_id).join(MarketplaceSellerProfile,MarketplaceSellerProfile.tenant_id==MarketplaceListing.seller_tenant_id).where(MarketplaceCartItem.cart_id==cart.id)).all()
        items=[]
        for ci,l,s in rows:
            items.append({'id':ci.id,'listing':self._listing_view(l,s),'quantity':str(ci.quantity),'line_total':str(_money(ci.quantity)*_money(l.unit_price))})
        return {'id':cart.id,'status':cart.status,'items':items}

    def checkout(self,user_id, shipping_address_id=None, shipping_fee=Decimal('0'), platform_fee_bps=500, shipping_quote_id=None, idempotency_key=None, tenant_id=None):
        try:
            return self._checkout(user_id, shipping_address_id, shipping_fee, platform_fee_bps, shipping_quote_id, idempotency_key, tenant_id)
        except Exception:
            self.db.rollback()
            raise

    def _checkout(self,user_id, shipping_address_id=None, shipping_fee=Decimal('0'), platform_fee_bps=500, shipping_quote_id=None, idempotency_key=None, tenant_id=None):
        if idempotency_key and not tenant_id:
            raise MarketplaceError('tenant context is required for idempotent checkout')
        self.db.rollback()
        cart=self.db.scalar(select(MarketplaceCart).where(MarketplaceCart.buyer_user_id==user_id,MarketplaceCart.status=='active').with_for_update())
        if cart is None:
            existing_cart=self.db.scalar(select(MarketplaceCart).where(MarketplaceCart.buyer_user_id==user_id))
            if existing_cart is not None: raise MarketplaceError('cart is not active')
            raise MarketplaceError('cart is empty')
        fingerprint=hashlib.sha256(json.dumps({'tenant_id':tenant_id,'user_id':user_id,'shipping_address_id':shipping_address_id,'shipping_fee':str(_money(shipping_fee)),'platform_fee_bps':platform_fee_bps,'shipping_quote_id':shipping_quote_id},sort_keys=True,separators=(',',':')).encode()).hexdigest()
        if idempotency_key:
            existing=self.db.scalar(select(IdempotencyRecord).where(IdempotencyRecord.tenant_id==tenant_id,IdempotencyRecord.key==idempotency_key))
            if existing:
                try:
                    ensure_same_request(IdempotencyResult(existing.key,existing.request_hash,201,{}),idempotency_key,fingerprint)
                except IdempotencyConflict as exc:
                    raise MarketplaceError('idempotency key was reused for a different checkout') from exc
                payload=json.loads(existing.response_json)
                orders=self.db.scalars(select(MarketplaceOrder).where(MarketplaceOrder.id.in_(payload['order_ids']),MarketplaceOrder.buyer_user_id==user_id)).all()
                if len(orders)!=len(payload['order_ids']): raise MarketplaceError('idempotency result is incomplete')
                return sorted(orders,key=lambda order: order.id)
        rows=self.db.execute(select(MarketplaceCartItem,MarketplaceListing,MarketplaceSellerProfile).join(MarketplaceListing,MarketplaceListing.id==MarketplaceCartItem.listing_id).join(MarketplaceSellerProfile,MarketplaceSellerProfile.tenant_id==MarketplaceListing.seller_tenant_id).join(MarketplaceSellerVerification,MarketplaceSellerVerification.seller_tenant_id==MarketplaceListing.seller_tenant_id).where(MarketplaceCartItem.cart_id==cart.id,MarketplaceListing.status=='published',MarketplaceListing.moderation_status=='approved',MarketplaceSellerProfile.status=='active',MarketplaceSellerVerification.status=='approved')).all()
        if not rows: raise MarketplaceError('cart is empty')
        rows=self.db.execute(select(MarketplaceCartItem,MarketplaceListing,MarketplaceSellerProfile).join(MarketplaceListing,MarketplaceListing.id==MarketplaceCartItem.listing_id).join(MarketplaceSellerProfile,MarketplaceSellerProfile.tenant_id==MarketplaceListing.seller_tenant_id).join(MarketplaceSellerVerification,MarketplaceSellerVerification.seller_tenant_id==MarketplaceListing.seller_tenant_id).where(MarketplaceCartItem.cart_id==cart.id,MarketplaceListing.status=='published',MarketplaceListing.moderation_status=='approved',MarketplaceSellerProfile.status=='active',MarketplaceSellerVerification.status=='approved')).all()
        if not rows: raise MarketplaceError('cart is empty')
        if shipping_address_id and not self.db.scalar(select(MarketplaceAddress).where(MarketplaceAddress.id==shipping_address_id,MarketplaceAddress.user_id==user_id,MarketplaceAddress.active.is_(True))): raise MarketplaceError('shipping address does not belong to buyer')
        quote=None
        if shipping_quote_id:
            quote=self.db.scalar(select(MarketplaceShippingQuote).where(MarketplaceShippingQuote.id==shipping_quote_id,MarketplaceShippingQuote.buyer_user_id==user_id).with_for_update())
            now=datetime.now(timezone.utc)
            expires=quote.expires_at.replace(tzinfo=timezone.utc) if quote and quote.expires_at.tzinfo is None else (quote.expires_at if quote else now)
            if not quote or quote.consumed_at or expires < now: raise MarketplaceError('shipping quote is invalid or expired')
            if shipping_address_id != quote.address_id: raise MarketplaceError('shipping quote does not match address')
            shipping_fee=_money(quote.fee)
        elif _money(shipping_fee) != Decimal('0'):
            raise MarketplaceError('shipping fee must come from a server-issued shipping quote')
        groups={}
        for ci,l,s in rows:
            groups.setdefault((s.tenant_id,l.currency),[]).append((ci,l,s))
        if shipping_quote_id and len(groups) != 1: raise MarketplaceError('one shipping quote is required per seller order; split checkout by seller')
        created=[]
        for (seller_id,currency), group in groups.items():
            subtotal=sum((_money(ci.quantity)*_money(l.unit_price) for ci,l,_ in group),Decimal('0'))
            fee=(_money(subtotal)*Decimal(platform_fee_bps)/Decimal(10000)).quantize(Decimal('0.0001'))
            total=subtotal+_money(shipping_fee)
            ref=f'MKT-{uuid4().hex[:20].upper()}'
            product_lines=[]
            for ci,l,_ in group:
                if l.listing_type=='product':
                    if l.stock_policy=='managed' and (_money(ci.quantity) > (self._stock(l) or Decimal('0'))): raise MarketplaceError(f'insufficient stock for listing {l.id}')
                    product_lines.append(OrderLineInput(item_id=l.item_id,quantity=_money(ci.quantity),unit_price=_money(l.unit_price)))
            sales=None
            if product_lines:
                # Commerce is authoritative for reservation; this stage is deliberately explicit and recoverable.
                wh=group[0][1].warehouse_id
                sales=CommerceProductionService(self.db).create_draft(tenant_id=seller_id,reference=f'MKT-SALE:{ref}',warehouse_id=wh,currency=currency,lines=product_lines,commit=False)
                CommerceProductionService(self.db).confirm(seller_id,sales.id,commit=False)
            order=MarketplaceOrder(reference=ref,buyer_user_id=user_id,seller_tenant_id=seller_id,sales_order_id=sales.id if sales else None,shipping_address_id=shipping_address_id,currency=currency,subtotal=subtotal,shipping_fee=_money(shipping_fee),platform_fee=fee,total=total,status='pending_payment')
            self.db.add(order); self.db.flush()
            sales_lines=self.db.scalars(select(SalesOrderLine).where(SalesOrderLine.order_id==sales.id).order_by(SalesOrderLine.id)) .all() if sales else []
            j=0
            for ci,l,_ in group:
                line_total=_money(ci.quantity)*_money(l.unit_price)
                self.db.add(MarketplaceOrderLine(marketplace_order_id=order.id,listing_id=l.id,sales_order_line_id=sales_lines[j].id if j<len(sales_lines) else None,title_snapshot=l.title,quantity=_money(ci.quantity),unit_price=_money(l.unit_price),line_total=line_total)); j+=1
            self.db.add(MarketplacePayout(seller_tenant_id=seller_id,marketplace_order_id=order.id,reference=f'PAYOUT:{ref}',gross_amount=total,platform_fee=fee,net_amount=total-fee,currency=currency,status='held'))
            self._event(seller_id,'marketplace.order.created','marketplace_order',order.id,{'reference':ref,'buyer_user_id':user_id,'total':str(total),'currency':currency})
            self.db.flush(); created.append(order)
            if quote: quote.consumed_at=datetime.now(timezone.utc)
        # A buyer owns one reusable active cart. Checkout materializes immutable orders, then clears the cart for the next purchase.
        for ci in list(self.db.scalars(select(MarketplaceCartItem).where(MarketplaceCartItem.cart_id==cart.id)).all()):
            self.db.delete(ci)
        cart.status='active'; cart.updated_at=datetime.now(timezone.utc)
        if idempotency_key:
            self.db.add(IdempotencyRecord(tenant_id=tenant_id,key=idempotency_key,request_hash=fingerprint,response_json=json.dumps({'order_ids':[order.id for order in created]},sort_keys=True)))
        try:
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            existing=self.db.scalar(select(IdempotencyRecord).where(IdempotencyRecord.tenant_id==tenant_id,IdempotencyRecord.key==idempotency_key)) if idempotency_key else None
            if existing and existing.request_hash==fingerprint:
                payload=json.loads(existing.response_json)
                return sorted(self.db.scalars(select(MarketplaceOrder).where(MarketplaceOrder.id.in_(payload['order_ids']),MarketplaceOrder.buyer_user_id==user_id)).all(),key=lambda order: order.id)
            raise MarketplaceError('checkout conflict')
        return created

    def _order(self, buyer_user_id, order_id, seller_tenant_id=None, lock=False):
        q=select(MarketplaceOrder).where(MarketplaceOrder.id==order_id)
        if buyer_user_id is not None: q=q.where(MarketplaceOrder.buyer_user_id==buyer_user_id)
        if seller_tenant_id is not None: q=q.where(MarketplaceOrder.seller_tenant_id==seller_tenant_id)
        if lock:q=q.with_for_update()
        x=self.db.scalar(q)
        if not x: raise MarketplaceError('marketplace order not found')
        return x

    def attach_payment_intent(self,buyer_user_id:str, order_id:int, provider:str):
        o=self._order(buyer_user_id,order_id,lock=True)
        if o.status!='pending_payment': raise MarketplaceError('order is not awaiting payment')
        if o.payment_reference: raise MarketplaceError('payment intent already exists for order')
        ref=f'MKT-PAY:{o.reference}'
        from app.engines.payments import PaymentProductionService
        p=PaymentProductionService(self.db).create_intent(o.seller_tenant_id,ref,provider,Decimal(str(o.total)),o.currency)
        o.payment_reference=p.reference; self.db.commit(); self.db.refresh(o)
        return p

    def mark_paid(self,seller_tenant_id:int, order_id:int, payment_reference:str):
        o=self._order(None,order_id,seller_tenant_id,True)
        if o.status!='pending_payment': raise MarketplaceError('order is not awaiting payment')
        p=self.db.scalar(select(PaymentIntent).where(PaymentIntent.tenant_id==seller_tenant_id,PaymentIntent.reference==payment_reference))
        if not p or p.status!='captured': raise MarketplaceError('payment must be captured before marketplace order is paid')
        if p.currency!=o.currency or _money(p.amount)!=_money(o.total): raise MarketplaceError('captured payment does not match marketplace order')
        o.status='paid'; o.payment_reference=payment_reference; o.updated_at=datetime.now(timezone.utc); self._event(seller_tenant_id,'marketplace.order.paid','marketplace_order',o.id,{'payment_reference':payment_reference}); self.db.commit(); return o

    def mark_processing(self,seller_tenant_id:int,order_id:int):
        o=self._order(None,order_id,seller_tenant_id,True)
        if o.status!='paid': raise MarketplaceError('only paid orders can enter processing')
        o.status='processing'; o.updated_at=datetime.now(timezone.utc); self._event(seller_tenant_id,'marketplace.order.processing','marketplace_order',o.id,{}); self.db.commit(); return o

    def mark_shipped(self,seller_tenant_id:int,order_id:int,shipment_id:int):
        o=self._order(None,order_id,seller_tenant_id,True)
        if o.status not in {'paid','processing'}: raise MarketplaceError('order cannot be marked shipped from current status')
        if not o.sales_order_id: raise MarketplaceError('service order has no shipment linkage')
        s=self.db.scalar(select(Shipment).where(Shipment.id==shipment_id,Shipment.tenant_id==seller_tenant_id,Shipment.order_id==o.sales_order_id))
        if not s: raise MarketplaceError('shipment does not belong to marketplace order')
        if s.status not in {'picked_up','in_transit','out_for_delivery','delivered'}: raise MarketplaceError('shipment is not in transit')
        o.status='delivered' if s.status=='delivered' else 'shipped'; o.updated_at=datetime.now(timezone.utc); self._event(seller_tenant_id,'marketplace.order.shipped','marketplace_order',o.id,{'shipment_id':shipment_id,'shipment_status':s.status}); self.db.commit(); return o

    def mark_delivered(self,seller_tenant_id:int,order_id:int,shipment_id:int):
        o=self._order(None,order_id,seller_tenant_id,True)
        if not o.sales_order_id: raise MarketplaceError('service order has no shipment')
        s=self.db.scalar(select(Shipment).where(Shipment.id==shipment_id,Shipment.tenant_id==seller_tenant_id,Shipment.order_id==o.sales_order_id,Shipment.status=='delivered'))
        if not s: raise MarketplaceError('delivered shipment not found')
        if o.status not in {'shipped','delivered'}: raise MarketplaceError('order is not in delivery state')
        o.status='completed'; o.updated_at=datetime.now(timezone.utc)
        p=self.db.scalar(select(MarketplacePayout).where(MarketplacePayout.marketplace_order_id==o.id,seller_tenant_id==MarketplacePayout.seller_tenant_id).with_for_update())
        if p and p.status=='held': p.status='eligible'; p.eligible_at=datetime.now(timezone.utc)
        self._event(seller_tenant_id,'marketplace.order.completed','marketplace_order',o.id,{'shipment_id':shipment_id}); self.db.commit(); return o

    def cancel(self,buyer_user_id,order_id):
        o=self._order(buyer_user_id,order_id,lock=True)
        if o.status != 'pending_payment': raise MarketplaceError('paid or processing orders require dispute/refund workflow; direct cancellation is not allowed')
        if o.sales_order_id:
            CommerceProductionService(self.db).cancel(o.seller_tenant_id,o.sales_order_id)
        o.status='cancelled'; o.updated_at=datetime.now(timezone.utc)
        p=self.db.scalar(select(MarketplacePayout).where(MarketplacePayout.marketplace_order_id==o.id))
        if p: p.status='reversed'
        self._event(o.seller_tenant_id,'marketplace.order.cancelled','marketplace_order',o.id,{}); self.db.commit(); return o

    def payout_eligible(self,seller_tenant_id:int,order_id:int):
        p=self.db.scalar(select(MarketplacePayout).where(MarketplacePayout.marketplace_order_id==order_id,MarketplacePayout.seller_tenant_id==seller_tenant_id).with_for_update())
        if not p: raise MarketplaceError('payout not found')
        if p.status!='eligible': raise MarketplaceError('payout is not eligible')
        return p

    def mark_payout_paid(self,seller_tenant_id:int,order_id:int,external_reference:str):
        p=self.payout_eligible(seller_tenant_id,order_id)
        destination=self.db.scalar(select(MarketplacePayoutDestination).where(MarketplacePayoutDestination.seller_tenant_id==seller_tenant_id))
        if not destination or destination.status!='verified': raise MarketplaceError('verified payout destination is required')
        if not external_reference: raise MarketplaceError('external payout reference required')
        p.status='paid'; p.paid_at=datetime.now(timezone.utc); self._event(seller_tenant_id,'marketplace.payout.paid','payout',p.id,{'external_reference':external_reference,'amount':str(p.net_amount),'currency':p.currency}); self.db.commit(); return p

    def create_review(self,buyer_user_id,order_id,listing_id,rating,title='',body=''):
        o=self._order(buyer_user_id,order_id)
        if o.status!='completed': raise MarketplaceError('review is available after completed order')
        line=self.db.scalar(select(MarketplaceOrderLine).where(MarketplaceOrderLine.marketplace_order_id==o.id,MarketplaceOrderLine.listing_id==listing_id))
        if not line: raise MarketplaceError('listing was not part of order')
        if self.db.scalar(select(MarketplaceReview).where(MarketplaceReview.marketplace_order_id==o.id,MarketplaceReview.listing_id==listing_id,MarketplaceReview.buyer_user_id==buyer_user_id)): raise MarketplaceError('review already exists')
        if rating<1 or rating>5: raise MarketplaceError('rating must be 1..5')
        x=MarketplaceReview(marketplace_order_id=o.id,listing_id=listing_id,buyer_user_id=buyer_user_id,rating=rating,title=title or '',body=body or '',status='published'); self.db.add(x); self._event(o.seller_tenant_id,'marketplace.review.created','review',x.id,{'listing_id':listing_id,'rating':rating}); self.db.commit(); return x

    def open_dispute(self,buyer_user_id,order_id,reason,description):
        o=self._order(buyer_user_id,order_id,lock=True)
        if o.status not in {'paid','processing','shipped','delivered','completed'}: raise MarketplaceError('order cannot be disputed in current status')
        if self.db.scalar(select(MarketplaceDispute).where(MarketplaceDispute.marketplace_order_id==o.id)): raise MarketplaceError('order already has a dispute')
        x=MarketplaceDispute(marketplace_order_id=o.id,opened_by_user_id=buyer_user_id,reason=reason,description=description,status='open'); self.db.add(x); o.status='disputed'; self._event(o.seller_tenant_id,'marketplace.dispute.opened','dispute',x.id,{'order_id':o.id,'reason':reason}); self.db.commit(); return x
