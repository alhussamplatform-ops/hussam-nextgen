from datetime import datetime, timezone
from sqlalchemy import Boolean, CheckConstraint, DateTime, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column
from app.core.persistence import Base


def now_utc(): return datetime.now(timezone.utc)

class MarketplaceSellerProfile(Base):
    __tablename__ = 'marketplace_seller_profiles'
    tenant_id: Mapped[int] = mapped_column(ForeignKey('tenants.id', ondelete='CASCADE'), primary_key=True)
    slug: Mapped[str] = mapped_column(String(120), nullable=False, unique=True)
    display_name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False, default='')
    seller_type: Mapped[str] = mapped_column(String(30), nullable=False, default='business')
    status: Mapped[str] = mapped_column(String(20), nullable=False, default='pending')
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc, nullable=False)
    __table_args__ = (
        CheckConstraint("seller_type IN ('business','individual','institution')", name='ck_market_seller_type'),
        CheckConstraint("status IN ('pending','active','suspended','closed')", name='ck_market_seller_status'),
    )

class MarketplaceCategory(Base):
    __tablename__ = 'marketplace_categories'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    parent_id: Mapped[int | None] = mapped_column(ForeignKey('marketplace_categories.id', ondelete='SET NULL'), nullable=True)
    slug: Mapped[str] = mapped_column(String(120), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

class MarketplaceListing(Base):
    __tablename__ = 'marketplace_listings'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    seller_tenant_id: Mapped[int] = mapped_column(ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False, index=True)
    item_id: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    warehouse_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    category_id: Mapped[int | None] = mapped_column(ForeignKey('marketplace_categories.id', ondelete='SET NULL'), nullable=True)
    slug: Mapped[str] = mapped_column(String(180), nullable=False)
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False, default='')
    listing_type: Mapped[str] = mapped_column(String(20), nullable=False, default='product')
    currency: Mapped[str] = mapped_column(String(10), nullable=False)
    unit_price: Mapped[object] = mapped_column(Numeric(20,4), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default='draft')
    stock_policy: Mapped[str] = mapped_column(String(20), nullable=False, default='managed')
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc, nullable=False)
    moderation_status: Mapped[str] = mapped_column(String(20), nullable=False, default='pending')
    __table_args__ = (
        UniqueConstraint('seller_tenant_id','slug', name='uq_market_listing_seller_slug'),
        CheckConstraint("listing_type IN ('product','service')", name='ck_market_listing_type'),
        CheckConstraint("status IN ('draft','published','paused','archived')", name='ck_market_listing_status'),
        CheckConstraint("moderation_status IN ('pending','approved','rejected','suspended')", name='ck_market_listing_moderation_status'),
        CheckConstraint("stock_policy IN ('managed','unmanaged')", name='ck_market_listing_stock_policy'),
        CheckConstraint('unit_price >= 0', name='ck_market_listing_price_nonnegative'),
        CheckConstraint("(listing_type = 'product' AND item_id IS NOT NULL AND warehouse_id IS NOT NULL) OR listing_type = 'service'", name='ck_market_listing_product_refs'),
        Index('ix_market_listing_public','status','category_id','seller_tenant_id'),
        Index('ix_market_listing_moderation','moderation_status','status'),
    )

class MarketplaceBuyerProfile(Base):
    __tablename__ = 'marketplace_buyer_profiles'
    user_id: Mapped[str] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'), primary_key=True)
    display_name: Mapped[str] = mapped_column(String(200), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc, nullable=False)

class MarketplaceAddress(Base):
    __tablename__ = 'marketplace_addresses'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    label: Mapped[str] = mapped_column(String(80), nullable=False)
    recipient_name: Mapped[str] = mapped_column(String(200), nullable=False)
    phone: Mapped[str] = mapped_column(String(50), nullable=False)
    governorate: Mapped[str] = mapped_column(String(120), nullable=False)
    city: Mapped[str] = mapped_column(String(120), nullable=False)
    address_line: Mapped[str] = mapped_column(String(500), nullable=False)
    landmark: Mapped[str | None] = mapped_column(String(300), nullable=True)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc, nullable=False)

class MarketplaceCart(Base):
    __tablename__ = 'marketplace_carts'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    buyer_user_id: Mapped[str] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'), nullable=False, unique=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default='active')
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc, nullable=False)
    __table_args__ = (CheckConstraint("status IN ('active','checked_out','abandoned')", name='ck_market_cart_status'),)

class MarketplaceCartItem(Base):
    __tablename__ = 'marketplace_cart_items'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    cart_id: Mapped[int] = mapped_column(ForeignKey('marketplace_carts.id', ondelete='CASCADE'), nullable=False, index=True)
    listing_id: Mapped[int] = mapped_column(ForeignKey('marketplace_listings.id', ondelete='RESTRICT'), nullable=False)
    quantity: Mapped[object] = mapped_column(Numeric(20,4), nullable=False)
    added_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc, nullable=False)
    __table_args__ = (UniqueConstraint('cart_id','listing_id', name='uq_market_cart_listing'), CheckConstraint('quantity > 0', name='ck_market_cart_quantity_positive'))

class MarketplaceOrder(Base):
    __tablename__ = 'marketplace_orders'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    reference: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    buyer_user_id: Mapped[str] = mapped_column(ForeignKey('users.id', ondelete='RESTRICT'), nullable=False, index=True)
    seller_tenant_id: Mapped[int] = mapped_column(ForeignKey('tenants.id', ondelete='RESTRICT'), nullable=False, index=True)
    sales_order_id: Mapped[int | None] = mapped_column(ForeignKey('sales_orders.id', ondelete='SET NULL'), nullable=True, unique=True)
    shipping_address_id: Mapped[int | None] = mapped_column(ForeignKey('marketplace_addresses.id', ondelete='SET NULL'), nullable=True)
    currency: Mapped[str] = mapped_column(String(10), nullable=False)
    subtotal: Mapped[object] = mapped_column(Numeric(20,4), nullable=False)
    shipping_fee: Mapped[object] = mapped_column(Numeric(20,4), nullable=False, default=0)
    platform_fee: Mapped[object] = mapped_column(Numeric(20,4), nullable=False, default=0)
    total: Mapped[object] = mapped_column(Numeric(20,4), nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default='pending_payment')
    payment_reference: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc, nullable=False)
    __table_args__ = (
        CheckConstraint("status IN ('pending_payment','paid','processing','shipped','delivered','completed','cancelled','refunded','disputed')", name='ck_market_order_status'),
        CheckConstraint('subtotal >= 0 AND shipping_fee >= 0 AND platform_fee >= 0 AND total >= 0', name='ck_market_order_amounts_nonnegative'),
    )

class MarketplaceOrderLine(Base):
    __tablename__ = 'marketplace_order_lines'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    marketplace_order_id: Mapped[int] = mapped_column(ForeignKey('marketplace_orders.id', ondelete='CASCADE'), nullable=False, index=True)
    listing_id: Mapped[int] = mapped_column(ForeignKey('marketplace_listings.id', ondelete='RESTRICT'), nullable=False)
    sales_order_line_id: Mapped[int | None] = mapped_column(ForeignKey('sales_order_lines.id', ondelete='SET NULL'), nullable=True)
    title_snapshot: Mapped[str] = mapped_column(String(300), nullable=False)
    quantity: Mapped[object] = mapped_column(Numeric(20,4), nullable=False)
    unit_price: Mapped[object] = mapped_column(Numeric(20,4), nullable=False)
    line_total: Mapped[object] = mapped_column(Numeric(20,4), nullable=False)
    __table_args__ = (CheckConstraint('quantity > 0 AND unit_price >= 0 AND line_total >= 0', name='ck_market_order_line_amounts'),)


class MarketplacePayoutDestination(Base):
    __tablename__ = 'marketplace_payout_destinations'
    seller_tenant_id: Mapped[int] = mapped_column(ForeignKey('tenants.id', ondelete='CASCADE'), primary_key=True)
    provider: Mapped[str] = mapped_column(String(80), nullable=False)
    external_reference: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default='pending')
    verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc, nullable=False)
    __table_args__ = (
        CheckConstraint("status IN ('pending','verified','disabled')", name='ck_market_payout_destination_status'),
        UniqueConstraint('provider','external_reference', name='uq_market_payout_destination_external'),
    )

class MarketplacePayout(Base):
    __tablename__ = 'marketplace_payouts'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    seller_tenant_id: Mapped[int] = mapped_column(ForeignKey('tenants.id', ondelete='RESTRICT'), nullable=False, index=True)
    marketplace_order_id: Mapped[int] = mapped_column(ForeignKey('marketplace_orders.id', ondelete='RESTRICT'), nullable=False, unique=True)
    reference: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    gross_amount: Mapped[object] = mapped_column(Numeric(20,4), nullable=False)
    platform_fee: Mapped[object] = mapped_column(Numeric(20,4), nullable=False)
    net_amount: Mapped[object] = mapped_column(Numeric(20,4), nullable=False)
    currency: Mapped[str] = mapped_column(String(10), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default='held')
    eligible_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    paid_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    __table_args__ = (CheckConstraint("status IN ('held','eligible','paid','reversed')", name='ck_market_payout_status'), CheckConstraint('gross_amount >= platform_fee AND net_amount = gross_amount - platform_fee', name='ck_market_payout_math'))

class MarketplaceReview(Base):
    __tablename__ = 'marketplace_reviews'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    marketplace_order_id: Mapped[int] = mapped_column(ForeignKey('marketplace_orders.id', ondelete='CASCADE'), nullable=False)
    listing_id: Mapped[int] = mapped_column(ForeignKey('marketplace_listings.id', ondelete='RESTRICT'), nullable=False)
    buyer_user_id: Mapped[str] = mapped_column(ForeignKey('users.id', ondelete='RESTRICT'), nullable=False)
    rating: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False, default='')
    body: Mapped[str] = mapped_column(Text, nullable=False, default='')
    status: Mapped[str] = mapped_column(String(20), nullable=False, default='published')
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc, nullable=False)
    __table_args__ = (UniqueConstraint('marketplace_order_id','listing_id','buyer_user_id', name='uq_market_review_once'), CheckConstraint('rating BETWEEN 1 AND 5', name='ck_market_review_rating'), CheckConstraint("status IN ('published','hidden','removed')", name='ck_market_review_status'))

class MarketplaceDispute(Base):
    __tablename__ = 'marketplace_disputes'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    marketplace_order_id: Mapped[int] = mapped_column(ForeignKey('marketplace_orders.id', ondelete='RESTRICT'), nullable=False, unique=True)
    opened_by_user_id: Mapped[str] = mapped_column(ForeignKey('users.id', ondelete='RESTRICT'), nullable=False)
    reason: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default='open')
    resolution: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc, nullable=False)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    __table_args__ = (CheckConstraint("status IN ('open','investigating','resolved','rejected','cancelled')", name='ck_market_dispute_status'),)

class MarketplaceSellerVerification(Base):
    __tablename__ = 'marketplace_seller_verifications'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    seller_tenant_id: Mapped[int] = mapped_column(ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default='pending')
    submitted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc, nullable=False)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    reviewer_user_id: Mapped[str | None] = mapped_column(ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    notes: Mapped[str] = mapped_column(Text, nullable=False, default='')
    __table_args__ = (UniqueConstraint('seller_tenant_id', name='uq_market_seller_verification_seller'), CheckConstraint("status IN ('pending','approved','rejected')", name='ck_market_seller_verification_status'))

class MarketplaceShippingRate(Base):
    __tablename__ = 'marketplace_shipping_rates'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    seller_tenant_id: Mapped[int] = mapped_column(ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False, index=True)
    governorate: Mapped[str] = mapped_column(String(120), nullable=False)
    city: Mapped[str | None] = mapped_column(String(120), nullable=True)
    currency: Mapped[str] = mapped_column(String(10), nullable=False)
    fee: Mapped[object] = mapped_column(Numeric(20,4), nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    __table_args__ = (UniqueConstraint('seller_tenant_id','governorate','city','currency',name='uq_market_shipping_rate'), CheckConstraint('fee >= 0', name='ck_market_shipping_fee_nonnegative'))

class MarketplaceShippingQuote(Base):
    __tablename__ = 'marketplace_shipping_quotes'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    buyer_user_id: Mapped[str] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    seller_tenant_id: Mapped[int] = mapped_column(ForeignKey('tenants.id', ondelete='RESTRICT'), nullable=False, index=True)
    address_id: Mapped[int] = mapped_column(ForeignKey('marketplace_addresses.id', ondelete='RESTRICT'), nullable=False)
    currency: Mapped[str] = mapped_column(String(10), nullable=False)
    fee: Mapped[object] = mapped_column(Numeric(20,4), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    consumed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    __table_args__ = (CheckConstraint('fee >= 0', name='ck_market_shipping_quote_fee_nonnegative'),)

class MarketplaceFavorite(Base):
    __tablename__ = 'marketplace_favorites'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    buyer_user_id: Mapped[str] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    listing_id: Mapped[int] = mapped_column(ForeignKey('marketplace_listings.id', ondelete='CASCADE'), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc, nullable=False)
    __table_args__ = (UniqueConstraint('buyer_user_id','listing_id',name='uq_market_favorite'),)

class MarketplaceReturnRequest(Base):
    __tablename__ = 'marketplace_return_requests'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    marketplace_order_id: Mapped[int] = mapped_column(ForeignKey('marketplace_orders.id', ondelete='RESTRICT'), nullable=False)
    opened_by_user_id: Mapped[str] = mapped_column(ForeignKey('users.id', ondelete='RESTRICT'), nullable=False)
    reason: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default='requested')
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now_utc, nullable=False)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    __table_args__ = (UniqueConstraint('marketplace_order_id',name='uq_market_return_order'), CheckConstraint("status IN ('requested','approved','rejected','received','refunded','cancelled')",name='ck_market_return_status'))
