from datetime import date
from decimal import Decimal
from fastapi import APIRouter,Depends
from pydantic import BaseModel,Field
from app.api.dependencies import get_context,get_session
from app.engines.finance.production import post_journal,PostingLine
router=APIRouter(prefix="/finance",tags=["finance"])
class Line(BaseModel):account_id:str;debit:Decimal=Field(default=0,ge=0);credit:Decimal=Field(default=0,ge=0)
class Journal(BaseModel):reference:str;currency:str;posting_date:date;lines:list[Line]=Field(min_length=2)
@router.post("/journals",status_code=201)
def journal(body:Journal,ctx=Depends(get_context),db=Depends(get_session)):
    x=post_journal(db,tenant_id=ctx.tenant_id,reference=body.reference,currency=body.currency,posting_date=body.posting_date,actor_id=ctx.user_id,lines=[PostingLine(**v.model_dump()) for v in body.lines]);db.commit();return {"id":x.id,"reference":x.reference,"status":x.status,"currency":x.currency}
