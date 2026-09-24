from app.services.pricing import calculate_api_cost_cents, calculate_token_cost_cents

def test_api_cost():
    assert calculate_api_cost_cents(10) == 10

def test_cached_input_is_not_fresh_input():
    assert calculate_token_cost_cents(1000, 500, 0, 0) == 1

def test_reasoning_counts_as_output():
    assert calculate_token_cost_cents(0, 0, 500, 500) == 2
