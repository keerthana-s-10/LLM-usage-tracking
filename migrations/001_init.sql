CREATE TABLE IF NOT EXISTS plans (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    api_calls_limit BIGINT NOT NULL CHECK (api_calls_limit >= 0),
    ai_tokens_limit BIGINT NOT NULL CHECK (ai_tokens_limit >= 0)
);

CREATE TABLE IF NOT EXISTS tenants (
    id UUID PRIMARY KEY,
    name TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS subscriptions (
    id UUID PRIMARY KEY,
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    plan_id TEXT NOT NULL REFERENCES plans(id),
    status TEXT NOT NULL CHECK (status IN ('active','past_due','canceled')),
    stripe_customer_id TEXT UNIQUE,
    stripe_subscription_id TEXT UNIQUE,
    current_period_start TIMESTAMPTZ,
    current_period_end TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE UNIQUE INDEX IF NOT EXISTS one_active_subscription_per_tenant
ON subscriptions(tenant_id) WHERE status <> 'canceled';

CREATE TABLE IF NOT EXISTS usage_events (
    id UUID PRIMARY KEY,
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    usage_type TEXT NOT NULL CHECK (usage_type IN ('api_calls','ai_tokens')),
    quantity BIGINT NOT NULL CHECK (quantity >= 0),
    ai_tokens BIGINT NOT NULL DEFAULT 0 CHECK (ai_tokens >= 0),
    input_tokens BIGINT NOT NULL DEFAULT 0 CHECK (input_tokens >= 0),
    cached_input_tokens BIGINT NOT NULL DEFAULT 0 CHECK (cached_input_tokens >= 0),
    output_tokens BIGINT NOT NULL DEFAULT 0 CHECK (output_tokens >= 0),
    reasoning_tokens BIGINT NOT NULL DEFAULT 0 CHECK (reasoning_tokens >= 0),
    idempotency_key TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE(tenant_id, idempotency_key)
);

CREATE INDEX IF NOT EXISTS usage_events_tenant_created_idx
ON usage_events(tenant_id, created_at);

CREATE TABLE IF NOT EXISTS processed_stripe_events (
    event_id TEXT PRIMARY KEY,
    event_type TEXT NOT NULL,
    processed_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS usage_rollups (
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    month_start DATE NOT NULL,
    api_calls_used BIGINT NOT NULL DEFAULT 0,
    ai_tokens_used BIGINT NOT NULL DEFAULT 0,
    cost_cents BIGINT NOT NULL DEFAULT 0,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (tenant_id, month_start)
);
