def signup_user(
    client,
    name,
    email,
    organization_name
):

    response = client.post(
        "/auth/signup",
        json={
            "name": name,
            "email": email,
            "password": "password123",
            "organization_name": organization_name
        }
    )

    assert response.status_code == 201

    return response.json()


def login_user(client, email):

    response = client.post(
        "/auth/login",
        json={
            "email": email,
            "password": "password123"
        }
    )

    assert response.status_code == 200

    return response.json()["access_token"]


def make_auth_header(token):

    return {
        "Authorization": f"Bearer {token}"
    }


def test_user_can_access_own_organization(client):

    # Create User A inside Organization A
    user_a = signup_user(
        client,
        name="User A",
        email="usera@example.com",
        organization_name="Organization A"
    )

    # Login as User A
    token_a = login_user(
        client,
        "usera@example.com"
    )

    org_a_id = user_a["org_id"]

    # User A tries to access Organization A
    response = client.get(
        f"/auth/organizations/{org_a_id}",
        headers=make_auth_header(token_a)
    )

    assert response.status_code == 200


def test_user_cannot_access_another_organization(client):

    # Create User A / Organization A
    user_a = signup_user(
        client,
        name="User A",
        email="usera@example.com",
        organization_name="Organization A"
    )

    # Create User B / Organization B
    user_b = signup_user(
        client,
        name="User B",
        email="userb@example.com",
        organization_name="Organization B"
    )

    # Login ONLY as User A
    token_a = login_user(
        client,
        "usera@example.com"
    )

    # Get Organization B ID
    org_b_id = user_b["org_id"]

    # Use User A token to try to access Organization B
    response = client.get(
        f"/auth/organizations/{org_b_id}",
        headers=make_auth_header(token_a)
    )

    # Must be forbidden
    assert response.status_code == 403