from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from app.domains.registry import DOMAINS
from app.api.routes import inventory, commerce, procurement, payments, documents, finance, logistics, workflow, session, dashboard, operations, retail, ai_hus, marketplace

VERSION="1.30.0"
app=FastAPI(title="Hussam Yemeni Sovereign Platform — NextGen",version=VERSION)

@app.exception_handler(ValueError)
async def domain_error_handler(request: Request, exc: ValueError):
    return JSONResponse(status_code=400, content={"detail": str(exc)})
app.include_router(inventory.router,prefix="/api/v1")
app.include_router(commerce.router,prefix="/api/v1")
app.include_router(procurement.router,prefix="/api/v1")
app.include_router(payments.router,prefix="/api/v1")
app.include_router(documents.router,prefix="/api/v1")
app.include_router(finance.router,prefix="/api/v1")
app.include_router(logistics.router,prefix="/api/v1")
app.include_router(workflow.router,prefix="/api/v1")
app.include_router(session.router,prefix="/api/v1")
app.include_router(dashboard.router,prefix="/api/v1")
app.include_router(operations.router,prefix="/api/v1")
app.include_router(retail.router,prefix="/api/v1")
app.include_router(ai_hus.router,prefix="/api/v1")
app.include_router(marketplace.router,prefix="/api/v1")
app.mount("/console", StaticFiles(directory="app/ui", html=True), name="console")

@app.get("/health")
def health(): return {"status":"ok","platform":"hussam-nextgen","version":VERSION}
@app.get("/api/v1/platform/manifest")
def manifest(): return {"domains":DOMAINS,"status":"api","version":VERSION,"architecture":{"core":"sovereign","engines":["identity","finance","inventory","commerce","procurement","payments","logistics","workflow","documents"],"verticals":["retail","marketplace"],"ai":"intelligence-v1.26+marketplace","hus_compiler":"operational-v1.1","marketplace":"complete-hardened-v1.29"}}
