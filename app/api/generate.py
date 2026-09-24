from fastapi import APIRouter, Header, HTTPException
from app.schemas import GenerateRequest
from app.services.metering import QuotaExceeded, record_generation

router = APIRouter(tags=["metering"])

@router.post("/generate")
def generate(body: GenerateRequest, x_tenant_id: str | None = Header(default=None), idempotency_key: str | None = Header(default=None)):
    if not x_tenant_id:
        raise HTTPException(400, "X-Tenant-ID header is required")
    if not idempotency_key:
        raise HTTPException(400, "Idempotency-Key header is required")
    try:
        result = record_generation(x_tenant_id, idempotency_key, body.tokens)
    except ValueError as exc:
        raise HTTPException(404, str(exc))
    except QuotaExceeded as exc:
        raise HTTPException(exc.status_code, detail={"message": exc.message, "used": exc.used, "limit": exc.limit})
    return {
        "message": "Billable action recorded" if not result["duplicate"] else "Idempotent replay: original event returned",
    }
