from decimal import Decimal
from sqlalchemy import select, func
from app.core.models.core import Journal, JournalLineRecord

def account_balance(session, *, tenant_id: int, account_id: str, currency: str) -> Decimal:
    debit = session.scalar(select(func.coalesce(func.sum(JournalLineRecord.debit), 0))
        .join(Journal, Journal.id == JournalLineRecord.journal_id)
        .where(Journal.tenant_id == tenant_id,
               JournalLineRecord.account == str(account_id),
               Journal.currency == currency))
    credit = session.scalar(select(func.coalesce(func.sum(JournalLineRecord.credit), 0))
        .join(Journal, Journal.id == JournalLineRecord.journal_id)
        .where(Journal.tenant_id == tenant_id,
               JournalLineRecord.account == str(account_id),
               Journal.currency == currency))
    return Decimal(str(debit or 0)) - Decimal(str(credit or 0))
