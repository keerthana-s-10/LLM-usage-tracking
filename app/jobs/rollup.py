import asyncio
import logging
from app.db.base import get_conn
from app.services.pricing import calculate_api_cost_cents, calculate_token_cost_cents

log = logging.getLogger(__name__)

def rollup_once():
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT tenant_id, date_trunc('month', created_at)::date AS month_start, "
            "COALESCE(SUM(CASE WHEN usage_type='api_calls' THEN quantity ELSE 0 END),0) api_calls, "
            "COALESCE(SUM(ai_tokens),0) ai_tokens, "
            "COALESCE(SUM(input_tokens),0) input_tokens, COALESCE(SUM(cached_input_tokens),0) cached_input_tokens, "
            "COALESCE(SUM(output_tokens),0) output_tokens, COALESCE(SUM(reasoning_tokens),0) reasoning_tokens "
            "FROM usage_events GROUP BY tenant_id, date_trunc('month', created_at)::date"
        ).fetchall()
        for row in rows:
            cost = calculate_api_cost_cents(int(row["api_calls"])) + calculate_token_cost_cents(
                int(row["input_tokens"]), int(row["cached_input_tokens"]),
                int(row["output_tokens"]), int(row["reasoning_tokens"])
            )
            conn.execute(
                "INSERT INTO usage_rollups(tenant_id,month_start,api_calls_used,ai_tokens_used,cost_cents) "
                "VALUES (%s,%s,%s,%s,%s) ON CONFLICT (tenant_id,month_start) DO UPDATE SET "
                "api_calls_used=EXCLUDED.api_calls_used, ai_tokens_used=EXCLUDED.ai_tokens_used, cost_cents=EXCLUDED.cost_cents, updated_at=now()",
                (row["tenant_id"], row["month_start"], row["api_calls"], row["ai_tokens"], cost),
            )

async def rollup_loop():
    while True:
        try:
            rollup_once()
        except Exception:
            log.exception("Background usage rollup failed")
        await asyncio.sleep(60)
