from fastapi import APIRouter, Header, HTTPException
from app.services.metering import get_usage

router = APIRouter(prefix="/usage", tags=["usage"])

@router.get("")
def usage(x_tenant_id: str | None = Header(default=None)):
    if not x_tenant_id:
        raise HTTPException(400, "X-Tenant-ID header is required")
    try:
        return get_usage(x_tenant_id)
    except ValueError as exc:
        raise HTTPException(404, str(exc))
