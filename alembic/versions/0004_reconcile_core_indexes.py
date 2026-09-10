"""reconcile ORM-declared tenant and inventory indexes"""
from alembic import op
revision='0004_reconcile_core_indexes'
down_revision='0003_procurement'
branch_labels=None
depends_on=None

def upgrade():
    indexes = [
        ('ix_audit_records_tenant_id','audit_records',['tenant_id']),
        ('ix_exchange_rates_tenant_id','exchange_rates',['tenant_id']),
        ('ix_fiscal_periods_tenant_id','fiscal_periods',['tenant_id']),
        ('ix_inventory_items_tenant_id','inventory_items',['tenant_id']),
        ('ix_inventory_movements_destination_warehouse_id','inventory_movements',['destination_warehouse_id']),
        ('ix_inventory_movements_item_id','inventory_movements',['item_id']),
        ('ix_inventory_movements_tenant_id','inventory_movements',['tenant_id']),
        ('ix_inventory_movements_warehouse_id','inventory_movements',['warehouse_id']),
        ('ix_inventory_reservations_item_id','inventory_reservations',['item_id']),
        ('ix_inventory_reservations_tenant_id','inventory_reservations',['tenant_id']),
        ('ix_inventory_reservations_warehouse_id','inventory_reservations',['warehouse_id']),
        ('ix_journal_lines_journal_id','journal_lines',['journal_id']),
        ('ix_journal_links_tenant_id','journal_links',['tenant_id']),
        ('ix_journals_tenant_id','journals',['tenant_id']),
        ('ix_suppliers_tenant_id','suppliers',['tenant_id']),
        ('ix_warehouses_tenant_id','warehouses',['tenant_id']),
    ]
    for name, table, cols in indexes:
        op.create_index(name, table, cols)

def downgrade():
    indexes = [
        ('ix_warehouses_tenant_id','warehouses'),('ix_suppliers_tenant_id','suppliers'),('ix_journals_tenant_id','journals'),
        ('ix_journal_links_tenant_id','journal_links'),('ix_journal_lines_journal_id','journal_lines'),
        ('ix_inventory_reservations_warehouse_id','inventory_reservations'),('ix_inventory_reservations_tenant_id','inventory_reservations'),('ix_inventory_reservations_item_id','inventory_reservations'),
        ('ix_inventory_movements_warehouse_id','inventory_movements'),('ix_inventory_movements_tenant_id','inventory_movements'),('ix_inventory_movements_item_id','inventory_movements'),('ix_inventory_movements_destination_warehouse_id','inventory_movements'),
        ('ix_inventory_items_tenant_id','inventory_items'),('ix_fiscal_periods_tenant_id','fiscal_periods'),('ix_exchange_rates_tenant_id','exchange_rates'),('ix_audit_records_tenant_id','audit_records')]
    for name, table in indexes: op.drop_index(name, table_name=table)
