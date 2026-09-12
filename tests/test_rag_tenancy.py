from app.api.services.vector_service import VectorService


def test_org_cannot_retrieve_another_org_documents():
    vector_service = VectorService()

    org_a_id = 1
    org_b_id = 2

    # Create two different vectors.
    # They don't need to come from the embedding model for this test.
    vector_a = [0.1] * 384
    vector_b = [0.2] * 384

    # Store a document chunk belonging to Org A
    vector_service.store_vector(
        vector=vector_a,
        document_id=100,
        org_id=org_a_id,
        chunk_index=0,
        text="Organization A secret information."
    )

    # Store a document chunk belonging to Org B
    vector_service.store_vector(
        vector=vector_b,
        document_id=200,
        org_id=org_b_id,
        chunk_index=0,
        text="Organization B secret information."
    )

    # Search as Org A
    results = vector_service.search_vectors(
        vector=vector_a,
        org_id=org_a_id,
        limit=10
    )

    # Org B's document must never appear
    document_ids = [
        result["document_id"]
        for result in results
    ]

    assert 100 in document_ids
    assert 200 not in document_ids

    # Also verify the actual content
    texts = [
        result["text"]
        for result in results
    ]

    assert "Organization A secret information." in texts
    assert "Organization B secret information." not in texts