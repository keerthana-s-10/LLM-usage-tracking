import uuid
import stripe
from app.config import settings
from app.db.base import get_conn

stripe.api_key = settings.stripe_secret_key

def create_checkout(tenant_id: str) -> str:
    if settings.stripe_secret_key.startswith("sk_test_replace"):
        raise RuntimeError("Configure STRIPE_SECRET_KEY before using Stripe Checkout")
    session = stripe.checkout.Session.create(
        mode="subscription",
        line_items=[{"price": settings.stripe_price_id, "quantity": 1}],
        metadata={"tenant_id": tenant_id},
        success_url="http://localhost:8000/docs?checkout=success",
        cancel_url="http://localhost:8000/docs?checkout=cancelled",
    )
    return session.url

def handle_event(event):
    event_id = event["id"]
    event_type = event["type"]
    with get_conn() as conn:
        already = conn.execute("SELECT 1 FROM processed_stripe_events WHERE event_id=%s", (event_id,)).fetchone()
        if already:
            return {"duplicate": True}
        obj = event["data"]["object"]
        if event_type == "checkout.session.completed":
            tenant_id = obj.get("metadata", {}).get("tenant_id")
            if tenant_id:
                conn.execute(
                    "UPDATE subscriptions SET plan_id='pro', status='active', stripe_customer_id=%s, stripe_subscription_id=%s, updated_at=now() "
                    "WHERE tenant_id=%s AND status <> 'canceled'",
                    (obj.get("customer"), obj.get("subscription"), tenant_id),
                )
        elif event_type in ("customer.subscription.updated", "customer.subscription.deleted"):
            stripe_sub_id = obj.get("id")
            tenant_id = conn.execute(
                "SELECT tenant_id FROM subscriptions WHERE stripe_subscription_id=%s",
                (stripe_sub_id,),
            ).fetchone()
            if tenant_id:
                status = "canceled" if event_type.endswith("deleted") else ("active" if obj.get("status") == "active" else "past_due")
                conn.execute(
                    "UPDATE subscriptions SET status=%s, updated_at=now() WHERE stripe_subscription_id=%s",
                    (status, stripe_sub_id),
                )
        conn.execute("INSERT INTO processed_stripe_events(event_id,event_type) VALUES (%s,%s)", (event_id,event_type))
        return {"duplicate": False}
