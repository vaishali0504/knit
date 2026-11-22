from fastapi.testclient import TestClient


def test_health_check_returns_ok(client: TestClient):
    """Test that GET /api/health returns 200 and expected schema."""
    response = client.get("/api/health")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "ok"
    assert data["app_name"] == "KNIT"
    assert "version" in data
    assert "environment" in data
    assert "timestamp" in data


def test_root_endpoint_returns_welcome(client: TestClient):
    """Test that GET / returns 200 and links to health."""
    response = client.get("/")
    assert response.status_code == 200

    data = response.json()
    assert "KNIT" in data["message"]
    assert data["health"] == "/api/health"
