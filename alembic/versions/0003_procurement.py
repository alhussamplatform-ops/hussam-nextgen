"""procurement and purchasing engine"""
from alembic import op
import sqlalchemy as sa
revision='0003_procurement'
down_revision='0002_commerce_orders'
branch_labels=None
depends_on=None

def upgrade():
    op.create_table('suppliers',
        sa.Column('id',sa.String(255),primary_key=True), sa.Column('tenant_id',sa.Integer(),sa.ForeignKey('tenants.id',ondelete='CASCADE'),primary_key=True,nullable=False),
        sa.Column('name',sa.String(255),nullable=False), sa.Column('active',sa.Boolean(),nullable=False,server_default=sa.true()),
        sa.UniqueConstraint('tenant_id','id',name='uq_supplier_tenant_id'))
    op.create_table('purchase_orders',
        sa.Column('id',sa.Integer(),primary_key=True), sa.Column('tenant_id',sa.Integer(),sa.ForeignKey('tenants.id',ondelete='CASCADE'),nullable=False),
        sa.Column('supplier_id',sa.String(255),nullable=False), sa.Column('warehouse_id',sa.String(255),nullable=False), sa.Column('reference',sa.String(255),nullable=False),
        sa.Column('currency',sa.String(10),nullable=False), sa.Column('status',sa.String(30),nullable=False), sa.Column('total',sa.Numeric(20,4),nullable=False),
        sa.Column('created_at',sa.DateTime(timezone=True),nullable=False), sa.Column('updated_at',sa.DateTime(timezone=True),nullable=False),
        sa.UniqueConstraint('tenant_id','reference',name='uq_purchase_order_tenant_reference'),
        sa.CheckConstraint("status IN ('draft','confirmed','cancelled','partially_received','received')",name='ck_purchase_order_status'),
        sa.CheckConstraint('total >= 0',name='ck_purchase_order_total_nonnegative'))
    op.create_index('ix_purchase_orders_tenant_id','purchase_orders',['tenant_id']); op.create_index('ix_purchase_orders_supplier_id','purchase_orders',['supplier_id']); op.create_index('ix_purchase_orders_warehouse_id','purchase_orders',['warehouse_id'])
    op.create_table('purchase_order_lines',
        sa.Column('id',sa.Integer(),primary_key=True), sa.Column('order_id',sa.Integer(),sa.ForeignKey('purchase_orders.id',ondelete='CASCADE'),nullable=False), sa.Column('tenant_id',sa.Integer(),sa.ForeignKey('tenants.id',ondelete='CASCADE'),nullable=False),
        sa.Column('item_id',sa.String(255),nullable=False), sa.Column('quantity',sa.Numeric(20,4),nullable=False), sa.Column('unit_cost',sa.Numeric(20,4),nullable=False), sa.Column('received_quantity',sa.Numeric(20,4),nullable=False), sa.Column('line_total',sa.Numeric(20,4),nullable=False),
        sa.CheckConstraint('quantity > 0',name='ck_purchase_line_positive_quantity'), sa.CheckConstraint('unit_cost >= 0',name='ck_purchase_line_nonnegative_cost'), sa.CheckConstraint('received_quantity >= 0',name='ck_purchase_line_nonnegative_received'), sa.CheckConstraint('received_quantity <= quantity',name='ck_purchase_line_received_lte_ordered'), sa.CheckConstraint('line_total >= 0',name='ck_purchase_line_nonnegative_total'))
    op.create_index('ix_purchase_order_lines_order_id','purchase_order_lines',['order_id']); op.create_index('ix_purchase_order_lines_tenant_id','purchase_order_lines',['tenant_id']); op.create_index('ix_purchase_order_lines_item_id','purchase_order_lines',['item_id'])
    op.create_table('purchase_receipts',
        sa.Column('id',sa.Integer(),primary_key=True), sa.Column('tenant_id',sa.Integer(),sa.ForeignKey('tenants.id',ondelete='CASCADE'),nullable=False), sa.Column('purchase_order_id',sa.Integer(),sa.ForeignKey('purchase_orders.id',ondelete='CASCADE'),nullable=False),
        sa.Column('reference',sa.String(255),nullable=False), sa.Column('currency',sa.String(10),nullable=False), sa.Column('total',sa.Numeric(20,4),nullable=False), sa.Column('status',sa.String(20),nullable=False), sa.Column('created_at',sa.DateTime(timezone=True),nullable=False),
        sa.UniqueConstraint('tenant_id','reference',name='uq_purchase_receipt_tenant_reference'), sa.CheckConstraint("status = 'posted'",name='ck_purchase_receipt_status'), sa.CheckConstraint('total >= 0',name='ck_purchase_receipt_total_nonnegative'))
    op.create_index('ix_purchase_receipts_tenant_id','purchase_receipts',['tenant_id']); op.create_index('ix_purchase_receipts_purchase_order_id','purchase_receipts',['purchase_order_id'])
    op.create_table('purchase_receipt_lines',
        sa.Column('id',sa.Integer(),primary_key=True), sa.Column('receipt_id',sa.Integer(),sa.ForeignKey('purchase_receipts.id',ondelete='CASCADE'),nullable=False), sa.Column('tenant_id',sa.Integer(),sa.ForeignKey('tenants.id',ondelete='CASCADE'),nullable=False), sa.Column('purchase_order_line_id',sa.Integer(),sa.ForeignKey('purchase_order_lines.id'),nullable=False),
        sa.Column('item_id',sa.String(255),nullable=False), sa.Column('quantity',sa.Numeric(20,4),nullable=False), sa.Column('unit_cost',sa.Numeric(20,4),nullable=False), sa.Column('line_total',sa.Numeric(20,4),nullable=False),
        sa.CheckConstraint('quantity > 0',name='ck_purchase_receipt_line_positive_quantity'), sa.CheckConstraint('unit_cost >= 0',name='ck_purchase_receipt_line_nonnegative_cost'), sa.CheckConstraint('line_total >= 0',name='ck_purchase_receipt_line_nonnegative_total'),
        sa.UniqueConstraint('tenant_id','purchase_order_line_id','receipt_id',name='uq_receipt_line_orderline_receipt'))
    op.create_index('ix_purchase_receipt_lines_receipt_id','purchase_receipt_lines',['receipt_id']); op.create_index('ix_purchase_receipt_lines_tenant_id','purchase_receipt_lines',['tenant_id']); op.create_index('ix_purchase_receipt_lines_purchase_order_line_id','purchase_receipt_lines',['purchase_order_line_id'])

def downgrade():
    for idx,table in [('ix_purchase_receipt_lines_purchase_order_line_id','purchase_receipt_lines'),('ix_purchase_receipt_lines_tenant_id','purchase_receipt_lines'),('ix_purchase_receipt_lines_receipt_id','purchase_receipt_lines')]: op.drop_index(idx,table_name=table)
    op.drop_table('purchase_receipt_lines')
    for idx,table in [('ix_purchase_receipts_purchase_order_id','purchase_receipts'),('ix_purchase_receipts_tenant_id','purchase_receipts')]: op.drop_index(idx,table_name=table)
    op.drop_table('purchase_receipts')
    for idx,table in [('ix_purchase_order_lines_item_id','purchase_order_lines'),('ix_purchase_order_lines_tenant_id','purchase_order_lines'),('ix_purchase_order_lines_order_id','purchase_order_lines')]: op.drop_index(idx,table_name=table)
    op.drop_table('purchase_order_lines')
    for idx,table in [('ix_purchase_orders_warehouse_id','purchase_orders'),('ix_purchase_orders_supplier_id','purchase_orders'),('ix_purchase_orders_tenant_id','purchase_orders')]: op.drop_index(idx,table_name=table)
    op.drop_table('purchase_orders'); op.drop_table('suppliers')
