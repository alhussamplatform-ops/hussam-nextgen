"""marketplace trust controls and AI/HUS integration
Revision ID: 0015_marketplace_trust_ai_integration
Revises: 0014_marketplace_completion
"""
from alembic import op
import sqlalchemy as sa
revision='0015_marketplace_trust_ai_integration'
down_revision='0014_marketplace_completion'
branch_labels=None
depends_on=None

def upgrade():
    op.add_column('marketplace_listings', sa.Column('moderation_status', sa.String(20), nullable=False, server_default='pending'))
    with op.batch_alter_table('marketplace_listings') as batch:
        batch.create_check_constraint('ck_market_listing_moderation_status',"moderation_status IN ('pending','approved','rejected','suspended')")
    # Preserve already-published listings during upgrade; new listings remain pending.
    op.execute("UPDATE marketplace_listings SET moderation_status='approved' WHERE status='published'")
    op.create_index('ix_market_listing_moderation','marketplace_listings',['moderation_status','status'])
    op.create_table('marketplace_payout_destinations',
        sa.Column('seller_tenant_id',sa.Integer(),sa.ForeignKey('tenants.id',ondelete='CASCADE'),primary_key=True),
        sa.Column('provider',sa.String(80),nullable=False),
        sa.Column('external_reference',sa.String(255),nullable=False),
        sa.Column('status',sa.String(20),nullable=False,server_default='pending'),
        sa.Column('verified_at',sa.DateTime(timezone=True)),
        sa.Column('created_at',sa.DateTime(timezone=True),nullable=False),
        sa.UniqueConstraint('provider','external_reference',name='uq_market_payout_destination_external'),
        sa.CheckConstraint("status IN ('pending','verified','disabled')",name='ck_market_payout_destination_status'))

def downgrade():
    op.drop_table('marketplace_payout_destinations')
    op.drop_index('ix_market_listing_moderation',table_name='marketplace_listings')
    with op.batch_alter_table('marketplace_listings') as batch:
        batch.drop_constraint('ck_market_listing_moderation_status',type_='check')
        batch.drop_column('moderation_status')
