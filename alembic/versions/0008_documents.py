from alembic import op
import sqlalchemy as sa

revision = "0008_documents"
down_revision = "0007_workflows"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "business_documents",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("tenant_id", sa.Integer(), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("document_type", sa.String(100), nullable=False),
        sa.Column("reference", sa.String(255), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("status", sa.String(30), nullable=False),
        sa.Column("current_version", sa.Integer(), nullable=False),
        sa.Column("metadata_json", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("finalized_at", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint("tenant_id", "reference", name="uq_business_document_tenant_reference"),
        sa.CheckConstraint("status IN ('draft','finalized','void')", name="ck_business_document_status"),
        sa.CheckConstraint("current_version >= 0", name="ck_business_document_version_nonnegative"),
    )
    op.create_index("ix_business_documents_tenant_id", "business_documents", ["tenant_id"])
    op.create_table(
        "document_versions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("tenant_id", sa.Integer(), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("document_id", sa.Integer(), sa.ForeignKey("business_documents.id", ondelete="CASCADE"), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("storage_key", sa.String(500), nullable=False),
        sa.Column("content_sha256", sa.String(64), nullable=False),
        sa.Column("content_type", sa.String(150), nullable=False),
        sa.Column("size_bytes", sa.Integer(), nullable=False),
        sa.Column("metadata_json", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("immutable", sa.Boolean(), nullable=False),
        sa.UniqueConstraint("tenant_id", "document_id", "version", name="uq_document_version_tenant_document_version"),
        sa.CheckConstraint("version > 0", name="ck_document_version_positive"),
        sa.CheckConstraint("size_bytes >= 0", name="ck_document_version_size_nonnegative"),
        sa.CheckConstraint("length(content_sha256) = 64", name="ck_document_version_sha256_length"),
    )
    op.create_index("ix_document_versions_tenant_id", "document_versions", ["tenant_id"])
    op.create_index("ix_document_versions_document_id", "document_versions", ["document_id"])
    op.create_table(
        "document_links",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("tenant_id", sa.Integer(), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("document_id", sa.Integer(), sa.ForeignKey("business_documents.id", ondelete="CASCADE"), nullable=False),
        sa.Column("aggregate_type", sa.String(100), nullable=False),
        sa.Column("aggregate_id", sa.String(255), nullable=False),
        sa.Column("relation", sa.String(100), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("tenant_id", "document_id", "aggregate_type", "aggregate_id", "relation", name="uq_document_link_unique_relation"),
    )
    op.create_index("ix_document_links_tenant_id", "document_links", ["tenant_id"])
    op.create_index("ix_document_links_document_id", "document_links", ["document_id"])


def downgrade():
    op.drop_index("ix_document_links_document_id", table_name="document_links")
    op.drop_index("ix_document_links_tenant_id", table_name="document_links")
    op.drop_table("document_links")
    op.drop_index("ix_document_versions_document_id", table_name="document_versions")
    op.drop_index("ix_document_versions_tenant_id", table_name="document_versions")
    op.drop_table("document_versions")
    op.drop_index("ix_business_documents_tenant_id", table_name="business_documents")
    op.drop_table("business_documents")
