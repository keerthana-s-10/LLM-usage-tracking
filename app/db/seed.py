import uuid
from app.db.base import get_conn

def seed():
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO plans (id,name,api_calls_limit,ai_tokens_limit) VALUES (%s,%s,%s,%s) "
            "ON CONFLICT (id) DO UPDATE SET name=EXCLUDED.name, api_calls_limit=EXCLUDED.api_calls_limit, ai_tokens_limit=EXCLUDED.ai_tokens_limit",
            ("free","Free",1000,100000),
        )
        conn.execute(
            "INSERT INTO plans (id,name,api_calls_limit,ai_tokens_limit) VALUES (%s,%s,%s,%s) "
            "ON CONFLICT (id) DO UPDATE SET name=EXCLUDED.name, api_calls_limit=EXCLUDED.api_calls_limit, ai_tokens_limit=EXCLUDED.ai_tokens_limit",
            ("pro","Pro",10000,1000000),
        )
        tenant_id = str(uuid.uuid4())
        conn.execute("INSERT INTO tenants(id,name) VALUES (%s,%s)", (tenant_id, "Demo Tenant"))
        conn.execute(
            "INSERT INTO subscriptions(id,tenant_id,plan_id,status) VALUES (%s,%s,%s,%s)",
            (str(uuid.uuid4()), tenant_id, "free", "active"),
        )
        return tenant_id

if __name__ == "__main__":
    print(seed())
