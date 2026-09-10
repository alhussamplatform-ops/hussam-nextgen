from alembic import op
import sqlalchemy as sa
revision='0012_ai_intelligence'; down_revision='0011_hus_operational'; branch_labels=None; depends_on=None

def upgrade():
    op.create_table('ai_insights',
        sa.Column('id',sa.String(64),primary_key=True), sa.Column('tenant_id',sa.Integer(),sa.ForeignKey('tenants.id',ondelete='CASCADE'),nullable=False,index=True),
        sa.Column('actor_id',sa.String(255),nullable=False), sa.Column('kind',sa.String(80),nullable=False), sa.Column('severity',sa.String(20),nullable=False),
        sa.Column('title',sa.String(500),nullable=False), sa.Column('evidence',sa.JSON(),nullable=False), sa.Column('status',sa.String(20),nullable=False,server_default='open'),
        sa.Column('created_at',sa.DateTime(timezone=True),nullable=False))
    op.create_table('ai_memories',
        sa.Column('id',sa.String(64),primary_key=True), sa.Column('tenant_id',sa.Integer(),sa.ForeignKey('tenants.id',ondelete='CASCADE'),nullable=False,index=True),
        sa.Column('actor_id',sa.String(255),nullable=False), sa.Column('key',sa.String(160),nullable=False), sa.Column('value',sa.JSON(),nullable=False),
        sa.Column('source',sa.String(40),nullable=False,server_default='user'), sa.Column('updated_at',sa.DateTime(timezone=True),nullable=False))
    op.create_index('ix_ai_memory_tenant_key','ai_memories',['tenant_id','key'],unique=True)
    op.create_table('ai_evaluations',
        sa.Column('id',sa.String(64),primary_key=True), sa.Column('tenant_id',sa.Integer(),sa.ForeignKey('tenants.id',ondelete='CASCADE'),nullable=False,index=True),
        sa.Column('actor_id',sa.String(255),nullable=False), sa.Column('run_id',sa.String(64),nullable=False,index=True), sa.Column('metric',sa.String(100),nullable=False),
        sa.Column('score',sa.Numeric(5,4),nullable=False), sa.Column('details',sa.JSON(),nullable=False), sa.Column('created_at',sa.DateTime(timezone=True),nullable=False))

def downgrade():
    op.drop_table('ai_evaluations'); op.drop_index('ix_ai_memory_tenant_key',table_name='ai_memories'); op.drop_table('ai_memories'); op.drop_table('ai_insights')
