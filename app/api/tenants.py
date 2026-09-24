import uuid
from fastapi import APIRouter, HTTPException
from app.db.base import get_conn
from app.schemas import TenantCreate

router = APIRouter(prefix="/tenants", tags=["tenants"])

@router.post("", status_code=201)
def create_tenant(body: TenantCreate):
    tenant_id = str(uuid.uuid4())
    with get_conn() as conn:
        conn.execute("INSERT INTO tenants(id,name) VALUES (%s,%s)", (tenant_id, body.name))
        conn.execute("INSERT INTO subscriptions(id,tenant_id,plan_id,status) VALUES (%s,%s,'free','active')", (str(uuid.uuid4()), tenant_id))
    return {"tenant_id": tenant_id, "plan": "free"}
