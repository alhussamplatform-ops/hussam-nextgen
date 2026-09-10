"""payments, webhooks, settlements and reconciliation"""
from alembic import op
import sqlalchemy as sa
revision='0005_payments'
down_revision='0004_reconcile_core_indexes'
branch_labels=None
depends_on=None

def upgrade():
    op.create_table('payment_intents',
        sa.Column('id',sa.Integer(),primary_key=True),
        sa.Column('tenant_id',sa.Integer(),sa.ForeignKey('tenants.id',ondelete='CASCADE'),nullable=False),
        sa.Column('reference',sa.String(255),nullable=False), sa.Column('provider',sa.String(80),nullable=False),
        sa.Column('amount',sa.Numeric(20,4),nullable=False), sa.Column('currency',sa.String(10),nullable=False),
        sa.Column('status',sa.String(30),nullable=False), sa.Column('provider_payment_id',sa.String(255)),
        sa.Column('metadata_json',sa.String(4000),nullable=False), sa.Column('created_at',sa.DateTime(timezone=True),nullable=False),
        sa.Column('updated_at',sa.DateTime(timezone=True),nullable=False),
        sa.UniqueConstraint('tenant_id','reference',name='uq_payment_intent_tenant_reference'),
        sa.UniqueConstraint('tenant_id','provider','provider_payment_id',name='uq_payment_intent_provider_payment'),
        sa.CheckConstraint('amount > 0',name='ck_payment_intent_positive_amount'),
        sa.CheckConstraint("status IN ('pending','processing','authorized','captured','failed','cancelled','refunded')",name='ck_payment_intent_status'))
    for name, table, col in [('ix_payment_intents_tenant_id','payment_intents','tenant_id')]: op.create_index(name,table,[col])
    op.create_table('payment_webhooks',
        sa.Column('id',sa.Integer(),primary_key=True), sa.Column('tenant_id',sa.Integer(),sa.ForeignKey('tenants.id',ondelete='CASCADE'),nullable=False),
        sa.Column('provider',sa.String(80),nullable=False), sa.Column('event_id',sa.String(255),nullable=False), sa.Column('event_type',sa.String(120),nullable=False),
        sa.Column('payment_reference',sa.String(255),nullable=False), sa.Column('payload_json',sa.String(10000),nullable=False),
        sa.Column('processed',sa.Boolean(),nullable=False), sa.Column('created_at',sa.DateTime(timezone=True),nullable=False),
        sa.UniqueConstraint('tenant_id','provider','event_id',name='uq_payment_webhook_event'))
    op.create_index('ix_payment_webhooks_tenant_id','payment_webhooks',['tenant_id'])
    op.create_table('payment_settlements',
        sa.Column('id',sa.Integer(),primary_key=True), sa.Column('tenant_id',sa.Integer(),sa.ForeignKey('tenants.id',ondelete='CASCADE'),nullable=False),
        sa.Column('provider',sa.String(80),nullable=False), sa.Column('settlement_reference',sa.String(255),nullable=False),
        sa.Column('payment_reference',sa.String(255),nullable=False), sa.Column('amount',sa.Numeric(20,4),nullable=False), sa.Column('currency',sa.String(10),nullable=False),
        sa.Column('status',sa.String(20),nullable=False), sa.Column('settled_at',sa.DateTime(timezone=True)),
        sa.UniqueConstraint('tenant_id','settlement_reference',name='uq_payment_settlement_tenant_reference'),
        sa.CheckConstraint('amount > 0',name='ck_payment_settlement_positive_amount'),
        sa.CheckConstraint("status IN ('pending','settled','reversed')",name='ck_payment_settlement_status'))
    op.create_index('ix_payment_settlements_tenant_id','payment_settlements',['tenant_id'])
    op.create_table('payment_reconciliations',
        sa.Column('id',sa.Integer(),primary_key=True), sa.Column('tenant_id',sa.Integer(),sa.ForeignKey('tenants.id',ondelete='CASCADE'),nullable=False),
        sa.Column('provider',sa.String(80),nullable=False), sa.Column('provider_reference',sa.String(255),nullable=False), sa.Column('internal_reference',sa.String(255)),
        sa.Column('expected_amount',sa.Numeric(20,4)), sa.Column('actual_amount',sa.Numeric(20,4),nullable=False), sa.Column('currency',sa.String(10),nullable=False),
        sa.Column('status',sa.String(30),nullable=False), sa.Column('details_json',sa.String(4000),nullable=False), sa.Column('created_at',sa.DateTime(timezone=True),nullable=False),
        sa.UniqueConstraint('tenant_id','provider','provider_reference',name='uq_payment_reconciliation_provider_ref'),
        sa.CheckConstraint("status IN ('matched','amount_mismatch','currency_mismatch','unknown')",name='ck_payment_reconciliation_status'))
    op.create_index('ix_payment_reconciliations_tenant_id','payment_reconciliations',['tenant_id'])

def downgrade():
    for name, table in [('ix_payment_reconciliations_tenant_id','payment_reconciliations'),('ix_payment_settlements_tenant_id','payment_settlements'),('ix_payment_webhooks_tenant_id','payment_webhooks'),('ix_payment_intents_tenant_id','payment_intents')]: op.drop_index(name,table_name=table)
    op.drop_table('payment_reconciliations'); op.drop_table('payment_settlements'); op.drop_table('payment_webhooks'); op.drop_table('payment_intents')
