# One-page design

## Problem
SaaS tenants need a reliable answer to how much they used, whether they are within plan limits, and what the current usage costs.

## Data model
- `tenants`: customer organizations.
- `plans`: quota definitions.
- `subscriptions`: the current plan/status mirrored from Stripe.
- `usage_events`: immutable billable events with idempotency keys and token categories.
- `processed_stripe_events`: webhook deduplication.
- `usage_rollups`: monthly derived summaries.

## API surface
- `POST /tenants`
- `POST /generate`
- `GET /usage`
- `POST /billing/checkout`
- `POST /webhooks/stripe`
- `GET /health`

## Idempotency
`(tenant_id, idempotency_key)` is unique. The service checks for an existing event before quota mutation and the database constraint protects against concurrent duplicate inserts.

## Quotas
Quota is checked before inserting usage events. Crossing a monthly limit returns 429 with the current usage and configured limit.

## Money
All costs are integer cents. Token pricing is pinned in code so the same inputs always produce the same expected result.

## Layering
HTTP routers validate requests and map errors; services implement metering/pricing/Stripe behavior; database helpers own connections; SQL migration owns persistence.

## Non-goal
Real AI inference, invoicing, proration, and overage billing are outside the core scope.
