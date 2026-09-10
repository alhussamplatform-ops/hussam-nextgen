from alembic import op
import sqlalchemy as sa
revision = '0009_retail_vertical'
down_revision = '0008_documents'
branch_labels = None
depends_on = None

def upgrade():
    op.create_table('retail_customers',
        sa.Column('id', sa.String(255), primary_key=True), sa.Column('tenant_id', sa.Integer(), sa.ForeignKey('tenants.id', ondelete='CASCADE'), primary_key=True),
        sa.Column('name', sa.String(255), nullable=False), sa.Column('phone', sa.String(50)), sa.Column('customer_type', sa.String(20), nullable=False),
        sa.Column('credit_limit', sa.Numeric(20,4), nullable=False), sa.Column('active', sa.Boolean(), nullable=False), sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint('tenant_id','id',name='uq_retail_customer_tenant_id'), sa.CheckConstraint("customer_type IN ('individual','business')",name='ck_retail_customer_type'), sa.CheckConstraint('credit_limit >= 0',name='ck_retail_customer_credit_limit_nonnegative'))
    op.create_index('ix_retail_customers_tenant_id','retail_customers',['tenant_id'])
    op.create_table('retail_product_profiles',
        sa.Column('id',sa.Integer(),primary_key=True), sa.Column('tenant_id',sa.Integer(),sa.ForeignKey('tenants.id',ondelete='CASCADE'),nullable=False), sa.Column('item_id',sa.String(255),nullable=False),
        sa.Column('sku',sa.String(120),nullable=False), sa.Column('barcode',sa.String(120)), sa.Column('category',sa.String(160)), sa.Column('sellable',sa.Boolean(),nullable=False), sa.Column('created_at',sa.DateTime(timezone=True),nullable=False),
        sa.UniqueConstraint('tenant_id','item_id',name='uq_retail_profile_tenant_item'), sa.UniqueConstraint('tenant_id','sku',name='uq_retail_profile_tenant_sku'), sa.UniqueConstraint('tenant_id','barcode',name='uq_retail_profile_tenant_barcode'))
    op.create_index('ix_retail_product_profiles_tenant_id','retail_product_profiles',['tenant_id']); op.create_index('ix_retail_product_profiles_item_id','retail_product_profiles',['item_id'])
    op.create_table('retail_product_prices',
        sa.Column('id',sa.Integer(),primary_key=True), sa.Column('tenant_id',sa.Integer(),sa.ForeignKey('tenants.id',ondelete='CASCADE'),nullable=False), sa.Column('item_id',sa.String(255),nullable=False),
        sa.Column('currency',sa.String(10),nullable=False), sa.Column('unit_price',sa.Numeric(20,4),nullable=False), sa.Column('active',sa.Boolean(),nullable=False), sa.Column('created_at',sa.DateTime(timezone=True),nullable=False),
        sa.UniqueConstraint('tenant_id','item_id','currency',name='uq_retail_price_tenant_item_currency'), sa.CheckConstraint('unit_price >= 0',name='ck_retail_price_nonnegative'))
    op.create_index('ix_retail_product_prices_tenant_id','retail_product_prices',['tenant_id']); op.create_index('ix_retail_product_prices_item_id','retail_product_prices',['item_id'])
    op.create_table('retail_register_shifts',
        sa.Column('id',sa.Integer(),primary_key=True), sa.Column('tenant_id',sa.Integer(),sa.ForeignKey('tenants.id',ondelete='CASCADE'),nullable=False), sa.Column('register_id',sa.String(120),nullable=False),
        sa.Column('operator_id',sa.String(255),nullable=False), sa.Column('currency',sa.String(10),nullable=False), sa.Column('opening_cash',sa.Numeric(20,4),nullable=False), sa.Column('closing_cash',sa.Numeric(20,4)),
        sa.Column('status',sa.String(20),nullable=False), sa.Column('opened_at',sa.DateTime(timezone=True),nullable=False), sa.Column('closed_at',sa.DateTime(timezone=True)),
        sa.CheckConstraint('opening_cash >= 0',name='ck_retail_shift_opening_cash_nonnegative'), sa.CheckConstraint('closing_cash IS NULL OR closing_cash >= 0',name='ck_retail_shift_closing_cash_nonnegative'), sa.CheckConstraint("status IN ('open','closed')",name='ck_retail_shift_status'))
    op.create_index('ix_retail_register_shifts_tenant_id','retail_register_shifts',['tenant_id'])
    op.create_index('ix_retail_register_one_open','retail_register_shifts',['tenant_id','register_id'],unique=True,sqlite_where=sa.text("status = 'open'"))

def downgrade():
    op.drop_index('ix_retail_register_one_open',table_name='retail_register_shifts'); op.drop_index('ix_retail_register_shifts_tenant_id',table_name='retail_register_shifts'); op.drop_table('retail_register_shifts')
    op.drop_index('ix_retail_product_prices_item_id',table_name='retail_product_prices'); op.drop_index('ix_retail_product_prices_tenant_id',table_name='retail_product_prices'); op.drop_table('retail_product_prices')
    op.drop_index('ix_retail_product_profiles_item_id',table_name='retail_product_profiles'); op.drop_index('ix_retail_product_profiles_tenant_id',table_name='retail_product_profiles'); op.drop_table('retail_product_profiles')
    op.drop_index('ix_retail_customers_tenant_id',table_name='retail_customers'); op.drop_table('retail_customers')
