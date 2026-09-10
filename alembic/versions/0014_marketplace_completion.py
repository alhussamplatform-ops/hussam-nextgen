"""marketplace completion hardening

Revision ID: 0014_marketplace_completion
Revises: 0013_marketplace
"""
from alembic import op
import sqlalchemy as sa

revision='0014_marketplace_completion'
down_revision='0013_marketplace'
branch_labels=None
depends_on=None

def upgrade():
    op.create_table('marketplace_seller_verifications',
        sa.Column('id',sa.Integer(),primary_key=True),
        sa.Column('seller_tenant_id',sa.Integer(),sa.ForeignKey('tenants.id',ondelete='CASCADE'),nullable=False),
        sa.Column('status',sa.String(20),nullable=False,server_default='pending'),
        sa.Column('submitted_at',sa.DateTime(timezone=True),nullable=False),
        sa.Column('reviewed_at',sa.DateTime(timezone=True)),
        sa.Column('reviewer_user_id',sa.String(255),sa.ForeignKey('users.id',ondelete='SET NULL')),
        sa.Column('notes',sa.Text(),nullable=False,server_default=''),
        sa.UniqueConstraint('seller_tenant_id',name='uq_market_seller_verification_seller'),
        sa.CheckConstraint("status IN ('pending','approved','rejected')",name='ck_market_seller_verification_status'))
    op.create_index('ix_marketplace_seller_verifications_seller_tenant_id','marketplace_seller_verifications',['seller_tenant_id'])
    op.create_table('marketplace_shipping_rates',
        sa.Column('id',sa.Integer(),primary_key=True),
        sa.Column('seller_tenant_id',sa.Integer(),sa.ForeignKey('tenants.id',ondelete='CASCADE'),nullable=False),
        sa.Column('governorate',sa.String(120),nullable=False),sa.Column('city',sa.String(120)),
        sa.Column('currency',sa.String(10),nullable=False),sa.Column('fee',sa.Numeric(20,4),nullable=False),
        sa.Column('active',sa.Boolean(),nullable=False,server_default=sa.true()),
        sa.UniqueConstraint('seller_tenant_id','governorate','city','currency',name='uq_market_shipping_rate'),
        sa.CheckConstraint('fee >= 0',name='ck_market_shipping_fee_nonnegative'))
    op.create_index('ix_marketplace_shipping_rates_seller_tenant_id','marketplace_shipping_rates',['seller_tenant_id'])
    op.create_table('marketplace_shipping_quotes',
        sa.Column('id',sa.Integer(),primary_key=True),
        sa.Column('buyer_user_id',sa.String(255),sa.ForeignKey('users.id',ondelete='CASCADE'),nullable=False),
        sa.Column('seller_tenant_id',sa.Integer(),sa.ForeignKey('tenants.id',ondelete='RESTRICT'),nullable=False),
        sa.Column('address_id',sa.Integer(),sa.ForeignKey('marketplace_addresses.id',ondelete='RESTRICT'),nullable=False),
        sa.Column('currency',sa.String(10),nullable=False),sa.Column('fee',sa.Numeric(20,4),nullable=False),
        sa.Column('expires_at',sa.DateTime(timezone=True),nullable=False),sa.Column('consumed_at',sa.DateTime(timezone=True)),
        sa.CheckConstraint('fee >= 0',name='ck_market_shipping_quote_fee_nonnegative'))
    op.create_index('ix_marketplace_shipping_quotes_buyer_user_id','marketplace_shipping_quotes',['buyer_user_id'])
    op.create_index('ix_marketplace_shipping_quotes_seller_tenant_id','marketplace_shipping_quotes',['seller_tenant_id'])
    op.create_table('marketplace_favorites',
        sa.Column('id',sa.Integer(),primary_key=True),
        sa.Column('buyer_user_id',sa.String(255),sa.ForeignKey('users.id',ondelete='CASCADE'),nullable=False),
        sa.Column('listing_id',sa.Integer(),sa.ForeignKey('marketplace_listings.id',ondelete='CASCADE'),nullable=False),
        sa.Column('created_at',sa.DateTime(timezone=True),nullable=False),
        sa.UniqueConstraint('buyer_user_id','listing_id',name='uq_market_favorite'))
    op.create_table('marketplace_return_requests',
        sa.Column('id',sa.Integer(),primary_key=True),
        sa.Column('marketplace_order_id',sa.Integer(),sa.ForeignKey('marketplace_orders.id',ondelete='RESTRICT'),nullable=False),
        sa.Column('opened_by_user_id',sa.String(255),sa.ForeignKey('users.id',ondelete='RESTRICT'),nullable=False),
        sa.Column('reason',sa.String(120),nullable=False),sa.Column('description',sa.Text(),nullable=False),
        sa.Column('status',sa.String(20),nullable=False,server_default='requested'),
        sa.Column('created_at',sa.DateTime(timezone=True),nullable=False),sa.Column('resolved_at',sa.DateTime(timezone=True)),
        sa.UniqueConstraint('marketplace_order_id',name='uq_market_return_order'),
        sa.CheckConstraint("status IN ('requested','approved','rejected','received','refunded','cancelled')",name='ck_market_return_status'))

def downgrade():
    op.drop_table('marketplace_return_requests'); op.drop_table('marketplace_favorites')
    op.drop_index('ix_marketplace_shipping_quotes_seller_tenant_id',table_name='marketplace_shipping_quotes')
    op.drop_index('ix_marketplace_shipping_quotes_buyer_user_id',table_name='marketplace_shipping_quotes')
    op.drop_table('marketplace_shipping_quotes')
    op.drop_index('ix_marketplace_shipping_rates_seller_tenant_id',table_name='marketplace_shipping_rates')
    op.drop_table('marketplace_shipping_rates')
    op.drop_index('ix_marketplace_seller_verifications_seller_tenant_id',table_name='marketplace_seller_verifications')
    op.drop_table('marketplace_seller_verifications')
