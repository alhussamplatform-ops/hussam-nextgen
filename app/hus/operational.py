"""Persistence and activation lifecycle for compiled HUS contracts."""
from hashlib import sha256
from uuid import uuid4
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.core.models.ai_hus import HUSCompilation
from app.hus.compiler import compile_spec, HUSCompileError, canonical

def compile_and_store(db: Session, tenant_id: int, actor_id: str, spec: dict):
    result=compile_spec(spec)
    x=HUSCompilation(id=str(uuid4()),tenant_id=tenant_id,actor_id=actor_id,spec_version=spec['spec_version'],source_hash=result['source_hash'],contract_hash=result['contract_hash'],status='compiled',contract=result['contract'],diagnostics=[])
    db.add(x); db.commit(); db.refresh(x)
    return x, result

def activate(db: Session, tenant_id: int, actor_id: str, compilation_id: str):
    x=db.scalar(select(HUSCompilation).where(HUSCompilation.id==compilation_id,HUSCompilation.tenant_id==tenant_id).with_for_update())
    if not x: raise ValueError('HUS compilation not found in tenant')
    if x.status not in {'compiled','active'}: raise ValueError('only a compiled HUS contract can be activated')
    active=db.scalars(select(HUSCompilation).where(HUSCompilation.tenant_id==tenant_id,HUSCompilation.status=='active',HUSCompilation.id!=compilation_id).with_for_update()).all()
    for old in active: old.status='superseded'
    x.status='active'
    db.commit(); db.refresh(x)
    return x
