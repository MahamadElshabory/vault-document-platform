from app.models.document import Document


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


def create_document(
    db_session,
    org_id,
    filename="test.pdf"
):

    document = Document(
        org_id=org_id,
        filename=filename,
        storage_ref="test.pdf",
        status="completed"
    )

    db_session.add(document)
    db_session.commit()
    db_session.refresh(document)

    return document


def test_user_can_access_own_document_text(
    client,
    db_session
):

    user_a = signup_user(
        client,
        name="User A",
        email="usera@example.com",
        organization_name="Organization A"
    )

    token_a = login_user(
        client,
        "usera@example.com"
    )

    document_a = create_document(
        db_session,
        org_id=user_a["org_id"],
        filename="organization_a.pdf"
    )

    from app.api.routes import documents

    original_extract = documents.document_service.extract_pdf_text

    documents.document_service.extract_pdf_text = (
        lambda storage_ref:
        "Organization A private information."
    )

    try:

        response = client.get(
            f"/documents/{document_a.id}/text",
            headers=make_auth_header(token_a)
        )

        assert response.status_code == 200
        assert response.json()["document_id"] == document_a.id

    finally:

        documents.document_service.extract_pdf_text = original_extract


def test_user_cannot_access_another_org_document_text(
    client,
    db_session
):

    user_a = signup_user(
        client,
        name="User A",
        email="usera@example.com",
        organization_name="Organization A"
    )

    user_b = signup_user(
        client,
        name="User B",
        email="userb@example.com",
        organization_name="Organization B"
    )

    token_a = login_user(
        client,
        "usera@example.com"
    )

    document_b = create_document(
        db_session,
        org_id=user_b["org_id"],
        filename="organization_b.pdf"
    )

    response = client.get(
        f"/documents/{document_b.id}/text",
        headers=make_auth_header(token_a)
    )

    assert response.status_code == 403


def test_document_text_requires_authentication(
    client,
    db_session
):

    user_a = signup_user(
        client,
        name="User A",
        email="usera@example.com",
        organization_name="Organization A"
    )

    document_a = create_document(
        db_session,
        org_id=user_a["org_id"]
    )

    response = client.get(
        f"/documents/{document_a.id}/text"
    )

    assert response.status_code == 401
    
def test_user_can_access_own_document_status(
    client,
    db_session
):

    user_a = signup_user(
        client,
        name="User A",
        email="usera_status@example.com",
        organization_name="Organization A"
    )

    token_a = login_user(
        client,
        "usera_status@example.com"
    )

    document_a = create_document(
        db_session,
        org_id=user_a["org_id"],
        filename="organization_a.pdf"
    )

    response = client.get(
        f"/documents/{document_a.id}/status",
        headers=make_auth_header(token_a)
    )

    assert response.status_code == 200

    data = response.json()

    assert data["document_id"] == document_a.id
    assert data["status"] == "completed"
    
    
def test_user_cannot_access_another_org_document_status(
    client,
    db_session
):

    user_a = signup_user(
        client,
        name="User A",
        email="usera_status2@example.com",
        organization_name="Organization A"
    )

    user_b = signup_user(
        client,
        name="User B",
        email="userb_status2@example.com",
        organization_name="Organization B"
    )

    token_a = login_user(
        client,
        "usera_status2@example.com"
    )

    document_b = create_document(
        db_session,
        org_id=user_b["org_id"],
        filename="organization_b.pdf"
    )

    # User A attempts to access Organization B's document status
    response = client.get(
        f"/documents/{document_b.id}/status",
        headers=make_auth_header(token_a)
    )

    assert response.status_code == 403
    
    
def test_rag_search_does_not_return_another_org_documents(
    client,
    db_session
):

    # Create User A / Organization A
    user_a = signup_user(
        client,
        name="User A",
        email="usera_rag@example.com",
        organization_name="Organization A"
    )

    # Create User B / Organization B
    user_b = signup_user(
        client,
        name="User B",
        email="userb_rag@example.com",
        organization_name="Organization B"
    )

    token_a = login_user(
        client,
        "usera_rag@example.com"
    )

    # Create documents for both organizations
    document_a = create_document(
        db_session,
        org_id=user_a["org_id"],
        filename="organization_a.pdf"
    )

    document_b = create_document(
        db_session,
        org_id=user_b["org_id"],
        filename="organization_b.pdf"
    )

    # Replace the real embedding/search services with controlled test data
    from app.api.routes import documents

    original_create_embedding = (
        documents.embedding_service.create_embedding
    )

    original_search_vectors = (
        documents.vector_service.search_vectors
    )

    try:

        documents.embedding_service.create_embedding = (
            lambda text: [0.1] * 384
        )

        documents.vector_service.search_vectors = (
            lambda vector, org_id, limit=5: [
                {
                    "score": 0.99,
                    "document_id": document_a.id,
                    "chunk_index": 0,
                    "text": "Organization A private information."
                }
            ]
            if org_id == user_a["org_id"]
            else []
        )

        response = client.post(
            "/documents/search",
            json={
                "query": "What is the private information?"
            },
            headers=make_auth_header(token_a)
        )

        assert response.status_code == 200

        data = response.json()

        assert data["query"] == "What is the private information?"

        # Verify only Organization A's document was returned
        source_document_ids = [
            source["document_id"]
            for source in data["sources"]
        ]

        assert document_a.id in source_document_ids
        assert document_b.id not in source_document_ids

        # Verify Organization B's content was not returned
        source_texts = [
            source["text"]
            for source in data["sources"]
        ]

        assert "Organization A private information." in source_texts
        assert "Organization B private information." not in source_texts

    finally:

        documents.embedding_service.create_embedding = (
            original_create_embedding
        )

        documents.vector_service.search_vectors = (
            original_search_vectors
        )   