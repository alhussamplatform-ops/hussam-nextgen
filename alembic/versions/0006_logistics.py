"""logistics shipment engine"""
from alembic import op
import sqlalchemy as sa
revision='0006_logistics'
down_revision='0005_payments'
branch_labels=None
depends_on=None

def upgrade():
    op.create_table('shipments',
        sa.Column('id',sa.Integer(),primary_key=True),
        sa.Column('tenant_id',sa.Integer(),sa.ForeignKey('tenants.id',ondelete='CASCADE'),nullable=False),
        sa.Column('order_id',sa.Integer(),sa.ForeignKey('sales_orders.id',ondelete='RESTRICT'),nullable=False),
        sa.Column('reference',sa.String(255),nullable=False), sa.Column('origin_warehouse_id',sa.String(255),nullable=False),
        sa.Column('destination',sa.String(500),nullable=False), sa.Column('carrier',sa.String(120),nullable=False),
        sa.Column('tracking_number',sa.String(255)), sa.Column('status',sa.String(30),nullable=False),
        sa.Column('cod_amount',sa.Numeric(20,4),nullable=False,server_default='0'), sa.Column('currency',sa.String(10),nullable=False),
        sa.Column('created_at',sa.DateTime(timezone=True),nullable=False), sa.Column('updated_at',sa.DateTime(timezone=True),nullable=False),
        sa.UniqueConstraint('tenant_id','reference',name='uq_shipment_tenant_reference'),
        sa.UniqueConstraint('tenant_id','tracking_number',name='uq_shipment_tenant_tracking'),
        sa.CheckConstraint("status IN ('ready','picked_up','in_transit','out_for_delivery','delivered','failed','cancelled','returned')",name='ck_shipment_status'),
        sa.CheckConstraint('cod_amount >= 0',name='ck_shipment_cod_nonnegative'))
    op.create_index('ix_shipments_tenant_id','shipments',['tenant_id']); op.create_index('ix_shipments_order_id','shipments',['order_id']); op.create_index('ix_shipments_origin_warehouse_id','shipments',['origin_warehouse_id'])
    op.create_table('shipment_events',
        sa.Column('id',sa.Integer(),primary_key=True), sa.Column('tenant_id',sa.Integer(),sa.ForeignKey('tenants.id',ondelete='CASCADE'),nullable=False),
        sa.Column('shipment_id',sa.Integer(),sa.ForeignKey('shipments.id',ondelete='CASCADE'),nullable=False), sa.Column('event_id',sa.String(255),nullable=False),
        sa.Column('event_type',sa.String(80),nullable=False), sa.Column('location',sa.String(255)), sa.Column('note',sa.Text()),
        sa.Column('occurred_at',sa.DateTime(timezone=True),nullable=False), sa.UniqueConstraint('tenant_id','event_id',name='uq_shipment_event_tenant_event'))
    op.create_index('ix_shipment_events_tenant_id','shipment_events',['tenant_id']); op.create_index('ix_shipment_events_shipment_id','shipment_events',['shipment_id'])
    op.create_table('shipment_collections',
        sa.Column('id',sa.Integer(),primary_key=True), sa.Column('tenant_id',sa.Integer(),sa.ForeignKey('tenants.id',ondelete='CASCADE'),nullable=False),
        sa.Column('shipment_id',sa.Integer(),sa.ForeignKey('shipments.id',ondelete='CASCADE'),nullable=False), sa.Column('reference',sa.String(255),nullable=False),
        sa.Column('amount',sa.Numeric(20,4),nullable=False), sa.Column('currency',sa.String(10),nullable=False), sa.Column('status',sa.String(20),nullable=False),
        sa.Column('payment_reference',sa.String(255)), sa.Column('collected_at',sa.DateTime(timezone=True)),
        sa.UniqueConstraint('tenant_id','reference',name='uq_shipment_collection_tenant_reference'), sa.UniqueConstraint('tenant_id','shipment_id',name='uq_one_collection_per_shipment'),
        sa.CheckConstraint('amount > 0',name='ck_shipment_collection_positive_amount'), sa.CheckConstraint("status IN ('pending','collected','failed','cancelled')",name='ck_shipment_collection_status'))
    op.create_index('ix_shipment_collections_tenant_id','shipment_collections',['tenant_id']); op.create_index('ix_shipment_collections_shipment_id','shipment_collections',['shipment_id'])

def downgrade():
    for name,table in [('ix_shipment_collections_shipment_id','shipment_collections'),('ix_shipment_collections_tenant_id','shipment_collections'),('ix_shipment_events_shipment_id','shipment_events'),('ix_shipment_events_tenant_id','shipment_events'),('ix_shipments_origin_warehouse_id','shipments'),('ix_shipments_order_id','shipments'),('ix_shipments_tenant_id','shipments')]: op.drop_index(name,table_name=table)
    op.drop_table('shipment_collections'); op.drop_table('shipment_events'); op.drop_table('shipments')
