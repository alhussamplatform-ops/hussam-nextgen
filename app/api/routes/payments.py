from decimal import Decimal
import os
from fastapi import APIRouter,Depends,Header,HTTPException,Request
from pydantic import BaseModel,Field
from app.api.dependencies import get_context,get_session
from app.engines.payments import PaymentProductionService
router=APIRouter(prefix="/payments",tags=["payments"])
class Intent(BaseModel): reference:str;provider:str;amount:Decimal=Field(gt=0);currency:str
class Provider(BaseModel):provider_payment_id:str
@router.post("/intents",status_code=201)
def create(body:Intent,ctx=Depends(get_context),db=Depends(get_session)):
    x=PaymentProductionService(db).create_intent(ctx.tenant_id,body.reference,body.provider,body.amount,body.currency);return {"id":x.id,"reference":x.reference,"status":x.status,"amount":str(x.amount),"currency":x.currency}
@router.post("/intents/{reference}/processing")
def processing(reference:str,ctx=Depends(get_context),db=Depends(get_session)):
    x=PaymentProductionService(db).mark_processing(ctx.tenant_id,reference);return {"reference":x.reference,"status":x.status}
@router.post("/intents/{reference}/provider")
def provider(reference:str,body:Provider,ctx=Depends(get_context),db=Depends(get_session)):
    x=PaymentProductionService(db).attach_provider_payment(ctx.tenant_id,reference,body.provider_payment_id);return {"reference":x.reference,"provider_payment_id":x.provider_payment_id}

class Webhook(BaseModel):
    tenant_id:int
    provider:str; event_id:str; event_type:str; payment_reference:str; provider_payment_id:str; status:str; payload:dict|None=None
class Settlement(BaseModel):
    settlement_reference:str; actual_amount:Decimal=Field(gt=0); currency:str; posting_date:str

@router.post("/webhooks")
async def webhook(request:Request, body:Webhook, signature: str | None = Header(default=None, alias="X-Webhook-Signature"), db=Depends(get_session)):
    PaymentProductionService.verify_webhook_signature(await request.body(), signature or "", os.getenv("PAYMENT_WEBHOOK_SECRET", ""))
    x=PaymentProductionService(db).process_webhook(body.tenant_id, **body.model_dump(exclude={"tenant_id"})); return {"reference":x.reference,"status":x.status,"provider_payment_id":x.provider_payment_id}

@router.post("/intents/{reference}/capture")
def capture(reference:str, posting_date:str,ctx=Depends(get_context),db=Depends(get_session)):
    from datetime import date
    x=PaymentProductionService(db).capture(ctx.tenant_id, reference, posting_date=date.fromisoformat(posting_date), actor_id=ctx.user_id); return {"reference":x.reference,"status":x.status}

@router.post("/intents/{reference}/settle")
def settle(reference:str,body:Settlement,ctx=Depends(get_context),db=Depends(get_session)):
    from datetime import date
    x=PaymentProductionService(db).settle(ctx.tenant_id, reference, settlement_reference=body.settlement_reference, actual_amount=body.actual_amount, currency=body.currency, posting_date=date.fromisoformat(body.posting_date), actor_id=ctx.user_id); return {"reference":x.reference,"status":x.status}
