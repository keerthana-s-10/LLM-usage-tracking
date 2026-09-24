def test_health():
    from app.main import app
    assert any(route.path == "/health" for route in app.routes)
