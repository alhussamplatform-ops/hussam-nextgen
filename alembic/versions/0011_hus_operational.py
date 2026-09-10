from alembic import op
import sqlalchemy as sa
revision='0011_hus_operational'; down_revision='0010_ai_hus_foundation'; branch_labels=None; depends_on=None

def upgrade():
    op.add_column('hus_compilations', sa.Column('contract_hash', sa.String(64), nullable=True))
    # Existing v1.23 rows are valid contracts; backfill from stored JSON deterministically in application-independent SQL is DB-specific,
    # so they remain nullable during upgrade. New application writes always populate it.

def downgrade():
    op.drop_column('hus_compilations','contract_hash')
