# Integer cents per 1,000 tokens. Pinned for deterministic tests/evidence.
API_CALL_CENTS = 1
INPUT_TOKEN_CENTS_PER_1K = 1
CACHED_INPUT_TOKEN_CENTS_PER_1K = 0
OUTPUT_TOKEN_CENTS_PER_1K = 2

def ceil_div(n: int, d: int) -> int:
    return (n + d - 1) // d if n else 0

def calculate_token_cost_cents(
    input_tokens: int,
    cached_input_tokens: int,
    output_tokens: int,
    reasoning_tokens: int,
) -> int:
    # Cached input is priced separately; reasoning is included in output pricing.
    fresh_input = max(input_tokens - cached_input_tokens, 0)
    effective_output = output_tokens + reasoning_tokens
    return (
        ceil_div(fresh_input * INPUT_TOKEN_CENTS_PER_1K, 1000)
        + ceil_div(cached_input_tokens * CACHED_INPUT_TOKEN_CENTS_PER_1K, 1000)
        + ceil_div(effective_output * OUTPUT_TOKEN_CENTS_PER_1K, 1000)
    )

def calculate_api_cost_cents(api_calls: int) -> int:
    return api_calls * API_CALL_CENTS
