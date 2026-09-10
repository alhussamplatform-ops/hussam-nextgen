"""sales order commerce engine"""
from alembic import op
import sqlalchemy as sa

revision = '0002_commerce_orders'
down_revision = '0001_initial_core'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'sales_orders',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('tenant_id', sa.Integer(), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('reference', sa.String(255), nullable=False),
        sa.Column('warehouse_id', sa.String(255), nullable=False),
        sa.Column('currency', sa.String(10), nullable=False),
        sa.Column('status', sa.String(20), nullable=False),
        sa.Column('total', sa.Numeric(20, 4), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint('tenant_id', 'reference', name='uq_sales_order_tenant_reference'),
        sa.CheckConstraint("status IN ('draft','confirmed','cancelled','fulfilled')", name='ck_sales_order_status'),
        sa.CheckConstraint('total >= 0', name='ck_sales_order_total_nonnegative'),
    )
    op.create_index('ix_sales_orders_tenant_id', 'sales_orders', ['tenant_id'])
    op.create_table(
        'sales_order_lines',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('order_id', sa.Integer(), sa.ForeignKey('sales_orders.id', ondelete='CASCADE'), nullable=False),
        sa.Column('tenant_id', sa.Integer(), sa.ForeignKey('tenants.id', ondelete='CASCADE'), nullable=False),
        sa.Column('item_id', sa.String(255), nullable=False),
        sa.Column('quantity', sa.Numeric(20, 4), nullable=False),
        sa.Column('unit_price', sa.Numeric(20, 4), nullable=False),
        sa.Column('line_total', sa.Numeric(20, 4), nullable=False),
        sa.Column('reservation_id', sa.Integer(), sa.ForeignKey('inventory_reservations.id'), nullable=True),
        sa.CheckConstraint('quantity > 0', name='ck_sales_order_line_positive_quantity'),
        sa.CheckConstraint('unit_price >= 0', name='ck_sales_order_line_nonnegative_price'),
        sa.CheckConstraint('line_total >= 0', name='ck_sales_order_line_nonnegative_total'),
    )
    op.create_index('ix_sales_order_lines_order_id', 'sales_order_lines', ['order_id'])
    op.create_index('ix_sales_order_lines_tenant_id', 'sales_order_lines', ['tenant_id'])
    op.create_index('ix_sales_order_lines_item_id', 'sales_order_lines', ['item_id'])


def downgrade():
    op.drop_table('sales_order_lines')
    op.drop_index('ix_sales_orders_tenant_id', table_name='sales_orders')
    op.drop_table('sales_orders')
