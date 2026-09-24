# Architecture notes

The service intentionally uses one metering path, one read path, and one payment-sync path.

1. `POST /generate` accepts simulated token usage.
2. `metering.record_generation()` checks idempotency, reads the current plan/usage, enforces limits, and writes immutable usage events.
3. `GET /usage` aggregates the current month and calculates cost from pinned integer-cent pricing.
4. `POST /billing/checkout` creates a Stripe test-mode Checkout session.
5. `/webhooks/stripe` verifies the raw payload signature, deduplicates the event ID, then mirrors subscription state.
6. The background rollup periodically writes monthly summaries into `usage_rollups`.
