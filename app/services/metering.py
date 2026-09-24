from app.db.base import get_conn
from app.services.pricing import calculate_api_cost_cents, calculate_token_cost_cents

class QuotaExceeded(Exception):
    def __init__(self, status_code, message, used, limit):
        self.status_code = status_code
        self.message = message
        self.used = used
        self.limit = limit

def _plan_and_usage(conn, tenant_id):
    sub = conn.execute(
        "SELECT s.plan_id, s.status, p.api_calls_limit, p.ai_tokens_limit "
        "FROM subscriptions s JOIN plans p ON p.id=s.plan_id "
        "WHERE s.tenant_id=%s AND s.status <> 'canceled' ORDER BY s.updated_at DESC LIMIT 1",
        (tenant_id,),
    ).fetchone()
    if not sub:
        raise ValueError("Tenant has no active subscription")
    usage = conn.execute(
        "SELECT COALESCE(SUM(quantity),0) AS api_calls, COALESCE(SUM(ai_tokens),0) AS ai_tokens "
        "FROM usage_events WHERE tenant_id=%s AND created_at >= date_trunc('month', now())",
        (tenant_id,),
    ).fetchone()
    return sub, usage

def record_generation(tenant_id, idempotency_key, tokens):
    ai_tokens = tokens.input_tokens + tokens.cached_input_tokens + tokens.output_tokens + tokens.reasoning_tokens
    with get_conn() as conn:
        existing = conn.execute(
            "SELECT * FROM usage_events WHERE tenant_id=%s AND idempotency_key=%s",
            (tenant_id, idempotency_key),
        ).fetchone()
        if existing:
            return {"duplicate": True, "event_id": str(existing["id"]), "quantities": {"api_calls": existing["quantity"], "ai_tokens": existing["ai_tokens"]}}

        sub, usage = _plan_and_usage(conn, tenant_id)
        if sub["status"] != "active":
            raise QuotaExceeded(402, "Payment or active subscription required", usage["api_calls"], sub["api_calls_limit"])
        if usage["api_calls"] + 1 > sub["api_calls_limit"]:
            raise QuotaExceeded(429, "API call quota exceeded", usage["api_calls"], sub["api_calls_limit"])
        if usage["ai_tokens"] + ai_tokens > sub["ai_tokens_limit"]:
            raise QuotaExceeded(429, "AI token quota exceeded", usage["ai_tokens"], sub["ai_tokens_limit"])

        import uuid
        event_id = str(uuid.uuid4())
        conn.execute(
            "INSERT INTO usage_events(id,tenant_id,usage_type,quantity,ai_tokens,input_tokens,cached_input_tokens,output_tokens,reasoning_tokens,idempotency_key) "
            "VALUES (%s,%s,'api_calls',1,%s,%s,%s,%s,%s,%s)",
            (event_id, tenant_id, ai_tokens, tokens.input_tokens, tokens.cached_input_tokens, tokens.output_tokens, tokens.reasoning_tokens, idempotency_key),
        )
        return {"duplicate": False, "event_id": event_id, "quantities": {"api_calls": 1, "ai_tokens": ai_tokens}}

def get_usage(tenant_id):
    with get_conn() as conn:
        sub, usage = _plan_and_usage(conn, tenant_id)
        token_rows = conn.execute(
            "SELECT COALESCE(SUM(input_tokens),0) input_tokens, COALESCE(SUM(cached_input_tokens),0) cached_input_tokens, "
            "COALESCE(SUM(output_tokens),0) output_tokens, COALESCE(SUM(reasoning_tokens),0) reasoning_tokens "
            "FROM usage_events WHERE tenant_id=%s AND created_at >= date_trunc('month', now())",
            (tenant_id,),
        ).fetchone()
        api_cost = calculate_api_cost_cents(int(usage["api_calls"]))
        token_cost = calculate_token_cost_cents(
            int(token_rows["input_tokens"]), int(token_rows["cached_input_tokens"]),
            int(token_rows["output_tokens"]), int(token_rows["reasoning_tokens"])
        )
        return {
            "tenant_id": tenant_id,
            "plan": sub["plan_id"],
            "status": sub["status"],
            "api_calls": {"used": int(usage["api_calls"]), "limit": int(sub["api_calls_limit"])},
            "ai_tokens": {"used": int(usage["ai_tokens"]), "limit": int(sub["ai_tokens_limit"])},
            "cost_cents": api_cost + token_cost,
            "token_breakdown": {k: int(v) for k,v in token_rows.items()},
        }
