SIGNUP_URL = "/auth/signup"
LOGIN_URL = "/auth/login"
ME_URL = "/auth/users/me"


def create_user(client):

    return client.post(
        SIGNUP_URL,
        json={
            "name": "Omar",
            "email": "omar@example.com",
            "password": "password123",
            "organization_name": "Organization A"
        }
    )


def login_user(
    client,
    email="omar@example.com",
    password="password123"
):

    return client.post(
        LOGIN_URL,
        json={
            "email": email,
            "password": password
        }
    )


def test_signup_success(client):

    response = create_user(client)

    assert response.status_code == 201

    data = response.json()

    assert data["name"] == "Omar"
    assert data["email"] == "omar@example.com"
    assert "org_id" in data

    # Password must never be returned
    assert "password" not in data
    assert "hashed_password" not in data


def test_duplicate_signup(client):

    create_user(client)

    response = create_user(client)

    assert response.status_code == 409


def test_login_success(client):

    create_user(client)

    response = login_user(client)

    assert response.status_code == 200

    data = response.json()

    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client):

    create_user(client)

    response = login_user(
        client,
        password="wrongpassword"
    )

    assert response.status_code == 401


def test_login_unknown_email(client):

    response = login_user(
        client,
        email="unknown@example.com"
    )

    assert response.status_code == 401


def test_user_me_success(client):

    # Create user
    create_user(client)

    # Login
    login_response = login_user(client)

    # Take token returned from login
    token = login_response.json()["access_token"]

    # Send token to /user/me
    response = client.get(
        ME_URL,
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["name"] == "Omar"
    assert data["email"] == "omar@example.com"
    assert "org_id" in data


def test_user_me_without_token(client):

    response = client.get(ME_URL)

    assert response.status_code == 401


def test_user_me_invalid_token(client):

    response = client.get(
        ME_URL,
        headers={
            "Authorization": "Bearer this-is-not-a-real-token"
        }
    )

    assert response.status_code == 401