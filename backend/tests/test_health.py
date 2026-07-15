from app import create_app

def test_health_route_returns_ok():
    app = create_app()
    client = app.test_client()
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.is_json

    data = response.get_json()

    assert data["service"] == "backend"
    assert data["status"] == "ok"