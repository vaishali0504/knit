from fastapi.testclient import TestClient


def test_user_registration_success(client: TestClient):
    """Test successful user registration."""
    payload = {
        "email": "testuser@knit.app",
        "password": "strongpassword123",
        "full_name": "Test User",
    }
    response = client.post("/api/auth/register", json=payload)
    assert response.status_code == 201

    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == "testuser@knit.app"
    assert data["user"]["full_name"] == "Test User"
    assert "id" in data["user"]


def test_user_registration_duplicate_email(client: TestClient):
    """Test registering with an existing email returns 400."""
    payload = {
        "email": "testuser@knit.app",
        "password": "anotherpassword",
    }
    response = client.post("/api/auth/register", json=payload)
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]


def test_user_registration_short_password(client: TestClient):
    """Test registering with password < 6 characters fails validation."""
    payload = {
        "email": "shortpass@knit.app",
        "password": "123",
    }
    response = client.post("/api/auth/register", json=payload)
    assert response.status_code == 422


def test_user_login_success(client: TestClient):
    """Test successful login with registered credentials."""
    login_payload = {
        "email": "testuser@knit.app",
        "password": "strongpassword123",
    }
    response = client.post("/api/auth/login", json=login_payload)
    assert response.status_code == 200

    data = response.json()
    assert "access_token" in data
    assert data["user"]["email"] == "testuser@knit.app"


def test_user_login_incorrect_password(client: TestClient):
    """Test login with wrong password returns 401."""
    login_payload = {
        "email": "testuser@knit.app",
        "password": "wrongpassword!",
    }
    response = client.post("/api/auth/login", json=login_payload)
    assert response.status_code == 401
    assert "Incorrect email or password" in response.json()["detail"]


def test_user_login_nonexistent_email(client: TestClient):
    """Test login with unknown email returns 401."""
    login_payload = {
        "email": "nobody@knit.app",
        "password": "somepassword",
    }
    response = client.post("/api/auth/login", json=login_payload)
    assert response.status_code == 401


def test_auth_me_with_valid_token(client: TestClient):
    """Test retrieving current user profile with valid Bearer token."""
    # First login to get token
    login_res = client.post(
        "/api/auth/login",
        json={"email": "testuser@knit.app", "password": "strongpassword123"},
    )
    token = login_res.json()["access_token"]

    response = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "testuser@knit.app"
    assert data["full_name"] == "Test User"


def test_auth_me_missing_token(client: TestClient):
    """Test accessing protected /api/auth/me without token returns 401/403."""
    response = client.get("/api/auth/me")
    assert response.status_code in (401, 403)


def test_auth_me_invalid_token(client: TestClient):
    """Test accessing /api/auth/me with invalid token returns 401."""
    response = client.get(
        "/api/auth/me",
        headers={"Authorization": "Bearer invalid.token.value"},
    )
    assert response.status_code == 401
