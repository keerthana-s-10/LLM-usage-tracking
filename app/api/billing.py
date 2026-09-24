from fastapi import APIRouter, HTTPException
from app.schemas import CheckoutRequest
from app.services.stripe_service import create_checkout

router = APIRouter(prefix="/billing", tags=["billing"])

@router.post("/checkout")
def checkout(body: CheckoutRequest):
    try:
        return {"checkout_url": create_checkout(body.tenant_id)}
    except RuntimeError as exc:
        raise HTTPException(503, str(exc))
