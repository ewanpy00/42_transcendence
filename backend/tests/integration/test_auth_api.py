import asyncio

USER = {"email": "Alice@Example.com", "username": "alice", "password": "s3cret-pass"}


def register(client, **overrides):
    return client.post("/api/v1/auth/register", json={**USER, **overrides})


def login(client, email=USER["email"], password=USER["password"]):
    return client.post("/api/v1/auth/login", json={"email": email, "password": password})


def bearer(token):
    return {"Authorization": f"Bearer {token}"}


def test_register_returns_user_without_password(client):
    r = register(client)

    assert r.status_code == 201
    body = r.json()
    assert body["email"] == "alice@example.com"
    assert body["username"] == "alice"
    assert "password" not in body and "hashed_password" not in body


def test_register_duplicate_email_and_username(client):
    register(client)

    assert register(client, username="alice2").status_code == 409
    assert register(client, email="other@example.com", username="ALICE").status_code == 409


def test_register_validation_errors(client):
    r = register(client, email="not-an-email", password="short", username="a b")

    assert r.status_code == 422
    fields = {tuple(e["loc"]) for e in r.json()["error"]["details"]}
    assert fields == {("body", "email"), ("body", "password"), ("body", "username")}


def test_login_and_protected_route(client):
    register(client)
    tokens = login(client).json()

    assert tokens["token_type"] == "bearer"
    assert tokens["expires_in"] == 15 * 60
    me = client.get("/api/v1/auth/me", headers=bearer(tokens["access_token"]))
    assert me.status_code == 200
    assert me.json()["username"] == "alice"


def test_login_wrong_password_and_unknown_email(client):
    register(client)

    for r in (login(client, password="wrong-pass"), login(client, email="nobody@example.com")):
        assert r.status_code == 401
        assert r.json()["error"]["message"] == "Invalid email or password"
        assert r.headers["www-authenticate"] == "Bearer"


def test_protected_route_rejects_missing_and_bad_tokens(client):
    register(client)
    refresh_token = login(client).json()["refresh_token"]

    assert client.get("/api/v1/auth/me").status_code == 401
    assert client.get("/api/v1/auth/me", headers=bearer("garbage")).status_code == 401
    # A refresh token must not work as an access token.
    assert client.get("/api/v1/auth/me", headers=bearer(refresh_token)).status_code == 401


def test_refresh_rotates_tokens(client):
    register(client)
    old = login(client).json()

    r = client.post("/api/v1/auth/refresh", json={"refresh_token": old["refresh_token"]})
    assert r.status_code == 200
    new = r.json()
    assert new["refresh_token"] != old["refresh_token"]
    assert client.get("/api/v1/auth/me", headers=bearer(new["access_token"])).status_code == 200

    # The old refresh token is single-use.
    reused = client.post("/api/v1/auth/refresh", json={"refresh_token": old["refresh_token"]})
    assert reused.status_code == 401


def test_refresh_rejects_access_token(client):
    register(client)
    access = login(client).json()["access_token"]

    assert client.post("/api/v1/auth/refresh", json={"refresh_token": access}).status_code == 401


def test_logout_revokes_refresh_token(client):
    register(client)
    refresh_token = login(client).json()["refresh_token"]

    assert client.post("/api/v1/auth/logout", json={"refresh_token": refresh_token}).status_code == 204
    r = client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
    assert r.status_code == 401


def test_refresh_token_is_stored_with_ttl(client, redis):
    register(client)
    login(client)

    async def check():
        keys = await redis.keys("auth:refresh:*")
        assert len(keys) == 1
        ttl = await redis.ttl(keys[0])
        assert 0 < ttl <= 7 * 24 * 3600

    asyncio.run(check())


def test_auth_endpoints_in_openapi(client):
    paths = client.get("/api/openapi.json").json()["paths"]

    for path in ("register", "login", "refresh", "logout", "me"):
        assert f"/api/v1/auth/{path}" in paths
