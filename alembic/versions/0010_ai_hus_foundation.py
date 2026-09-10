from alembic import op
import sqlalchemy as sa
revision='0010_ai_hus_foundation'; down_revision='0009_retail_vertical'; branch_labels=None; depends_on=None

def upgrade():
    op.create_table('ai_tool_definitions',
        sa.Column('id',sa.Integer(),primary_key=True), sa.Column('tenant_id',sa.Integer(),sa.ForeignKey('tenants.id',ondelete='CASCADE'),nullable=False),
        sa.Column('code',sa.String(120),nullable=False),sa.Column('name',sa.String(200),nullable=False),sa.Column('description',sa.Text(),nullable=False),
        sa.Column('risk',sa.String(20),nullable=False),sa.Column('input_schema',sa.JSON(),nullable=False),sa.Column('enabled',sa.Boolean(),nullable=False),sa.Column('created_at',sa.DateTime(timezone=True),nullable=False),
        sa.UniqueConstraint('tenant_id','code',name='uq_ai_tool_tenant_code'))
    op.create_index('ix_ai_tool_definitions_tenant_id','ai_tool_definitions',['tenant_id'])
    op.create_table('ai_runs',
        sa.Column('id',sa.String(64),primary_key=True),sa.Column('tenant_id',sa.Integer(),sa.ForeignKey('tenants.id',ondelete='CASCADE'),nullable=False),sa.Column('actor_id',sa.String(255),nullable=False),
        sa.Column('purpose',sa.String(200),nullable=False),sa.Column('status',sa.String(30),nullable=False),sa.Column('model',sa.String(120)),sa.Column('input_hash',sa.String(64),nullable=False),sa.Column('output',sa.JSON()),sa.Column('created_at',sa.DateTime(timezone=True),nullable=False))
    op.create_index('ix_ai_runs_tenant_id','ai_runs',['tenant_id'])
    op.create_table('ai_actions',
        sa.Column('id',sa.String(64),primary_key=True),sa.Column('tenant_id',sa.Integer(),sa.ForeignKey('tenants.id',ondelete='CASCADE'),nullable=False),sa.Column('run_id',sa.String(64),sa.ForeignKey('ai_runs.id',ondelete='CASCADE'),nullable=False),
        sa.Column('tool_code',sa.String(120),nullable=False),sa.Column('risk',sa.String(20),nullable=False),sa.Column('arguments',sa.JSON(),nullable=False),sa.Column('status',sa.String(30),nullable=False),sa.Column('result',sa.JSON()),sa.Column('approved_by',sa.String(255)),sa.Column('created_at',sa.DateTime(timezone=True),nullable=False))
    op.create_index('ix_ai_actions_tenant_id','ai_actions',['tenant_id'])
    op.create_table('hus_compilations',
        sa.Column('id',sa.String(64),primary_key=True),sa.Column('tenant_id',sa.Integer(),sa.ForeignKey('tenants.id',ondelete='CASCADE'),nullable=False),sa.Column('actor_id',sa.String(255),nullable=False),
        sa.Column('spec_version',sa.String(30),nullable=False),sa.Column('source_hash',sa.String(64),nullable=False),sa.Column('status',sa.String(30),nullable=False),sa.Column('contract',sa.JSON()),sa.Column('diagnostics',sa.JSON(),nullable=False),sa.Column('created_at',sa.DateTime(timezone=True),nullable=False))
    op.create_index('ix_hus_compilations_tenant_id','hus_compilations',['tenant_id'])

def downgrade():
    op.drop_index('ix_hus_compilations_tenant_id',table_name='hus_compilations'); op.drop_table('hus_compilations')
    op.drop_index('ix_ai_actions_tenant_id',table_name='ai_actions'); op.drop_table('ai_actions')
    op.drop_index('ix_ai_runs_tenant_id',table_name='ai_runs'); op.drop_table('ai_runs')
    op.drop_index('ix_ai_tool_definitions_tenant_id',table_name='ai_tool_definitions'); op.drop_table('ai_tool_definitions')
