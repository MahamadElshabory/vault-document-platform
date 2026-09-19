from app.api.services.document_service import DocumentService
from app.models.document import Document


def test_document_ingestion_with_mocked_embeddings(
    db_session,
    monkeypatch
):

    document = Document(
        org_id=1,
        filename="test.pdf",
        storage_ref="test.pdf",
        status="pending"
    )

    db_session.add(document)
    db_session.commit()
    db_session.refresh(document)

    document_service = DocumentService()

    # Fake PDF text extraction
    monkeypatch.setattr(
        document_service,
        "extract_pdf_text",
        lambda storage_ref: (
            "Employees receive 30 days annual leave. "
            "Employees receive public holidays according to company policy."
        )
    )

    # Fake embedding
    fake_vector = [0.1] * 384

    monkeypatch.setattr(
        "app.api.services.document_service.embedding_service.create_embedding",
        lambda text: fake_vector
    )

    stored_vectors = []

    # Fake Qdrant storage
    def fake_store_vector(
        vector,
        document_id,
        org_id,
        chunk_index,
        text
    ):

        stored_vectors.append({
            "vector": vector,
            "document_id": document_id,
            "org_id": org_id,
            "chunk_index": chunk_index,
            "text": text
        })

    monkeypatch.setattr(
        "app.api.services.document_service.vector_service.store_vector",
        fake_store_vector
    )

    document_service.document_process(
        document=document,
        session=db_session
    )

    assert document.status == "completed"

    assert len(stored_vectors) > 0

    for stored in stored_vectors:

        assert stored["document_id"] == document.id
        assert stored["org_id"] == document.org_id
        assert len(stored["vector"]) == 384
        assert stored["text"]