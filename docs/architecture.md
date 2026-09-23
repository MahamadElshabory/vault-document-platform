# Vault Architecture

## 1. Overview

Vault is a multi-tenant document intelligence platform built with Python and FastAPI.

The system allows authenticated users to:

- Upload PDF documents
- Extract document text
- Split documents into chunks
- Generate vector embeddings
- Store vectors in Qdrant
- Search documents using semantic similarity
- Generate answers using an LLM

Organization ownership is used to isolate users and their documents.

---

## 2. System Architecture

    Client
      |
      v
    FastAPI API
      |
      +-------------------+
      |                   |
      v                   v
    Authentication      Documents
      |                   |
      v                   +--> PDF Extraction
    PostgreSQL            +--> OCR
                          +--> Chunking
                          +--> Embeddings
                          +--> Qdrant

    RAG Search
      |
      +--> Embedding
      +--> Organization-scoped Qdrant Search
      +--> Ollama
      +--> Answer


    Background Processing

    FastAPI
      |
      v
    Redis
      |
      v
    Celery Worker

---

## 3. Authentication

Vault uses JWT-based authentication.

The authentication flow is:

    User
     |
     v
    POST /auth/signup
     |
     v
    User + Organization
     |
     v
    PostgreSQL


    User
     |
     v
    POST /auth/login
     |
     v
    Verify email + password
     |
     v
    JWT access token
     |
     v
    Authenticated API requests

Passwords are hashed using `pwdlib` before being stored.

Raw passwords are not stored in the database.

JWT tokens contain:

- User ID
- Organization ID
- Expiration time

---

## 4. Multi-Tenancy

Each user belongs to an organization.

The relationship is:

    Organization
         |
         +---- User
         |
         +---- Documents

A user's organization is identified by `org_id`.

Authenticated requests use the organization associated with the current user.

Document access is checked against the user's organization:

    Current User
         |
         v
    current_user.org_id
         |
         v
    Document.org_id
         |
         +---- Match ------> Access allowed
         |
         +---- Different --> Access forbidden

The same organization filter is also applied to vector searches.

This prevents a user from retrieving document content belonging to another organization.

---

## 5. Document Ingestion

The document ingestion flow is:

    PDF Upload
        |
        v
    Validate PDF
        |
        v
    Save File
        |
        v
    Create Document Record
        |
        v
    Extract Text
        |
        +---- Normal PDF text
        |
        +---- OCR for pages without extractable text
        |
        v
    Chunk Text
        |
        v
    Generate Embeddings
        |
        v
    Store Vectors in Qdrant
        |
        v
    Document Completed

PDF processing uses:

- `pypdf`
- `PyMuPDF`
- `pytesseract`
- `Pillow`

If normal PDF text extraction does not produce text for a page, OCR is used as a fallback.

---

## 6. Text Chunking

Extracted document text is divided into smaller chunks before creating embeddings.

The current document processing configuration uses:

    Chunk size: 1000 words
    Overlap: 200 words

The overlap helps preserve context between neighboring chunks.

---

## 7. Embeddings

Vault uses Sentence Transformers to convert text into numerical vectors.

The current embedding model is:

    all-MiniLM-L6-v2

The generated vectors contain:

    384 dimensions

These vectors are stored in Qdrant together with document metadata.

---

## 8. Qdrant Vector Storage

Qdrant stores document chunk embeddings.

Each stored vector contains metadata including:

    document_id
    org_id
    chunk_index
    text

The vector collection is:

    document_chunks

Searches use cosine similarity and an organization filter.

    Query
      |
      v
    Query Embedding
      |
      v
    Qdrant
      |
      +--> org_id filter
      |
      +--> Similarity search
      |
      v
    Relevant document chunks

---

## 9. RAG Pipeline

Vault uses Retrieval-Augmented Generation (RAG).

The complete question-answering flow is:

    User Question
          |
          v
    Create Query Embedding
          |
          v
    Qdrant Vector Search
          |
          v
    Filter by Organization
          |
          v
    Retrieve Relevant Chunks
          |
          v
    Build Context
          |
          v
    Send Context + Question
          |
          v
    Ollama
          |
          v
    Generated Answer

The LLM is instructed to answer using the retrieved document context.

If no relevant documents are found, the API returns:

    I couldn't find the answer in the provided documents.

---

## 10. Ollama

The LLM integration is separated behind an `LLMProvider` interface.

The current implementation uses:

    OllamaProvider

The configured model is provided through the application settings.

This separation allows the LLM implementation to be replaced without changing the document search API.

---

## 11. Background Processing

Redis and Celery are included for background document processing.

    FastAPI
       |
       v
    Celery Task
       |
       v
    Redis
       |
       v
    Celery Worker

The project currently contains a `process_document` Celery task.

---

## 12. Database

PostgreSQL stores the application's primary relational data.

Main entities include:

    organizations
    users
    documents

Relationships:

    Organization
        |
        +---- Users
        |
        +---- Documents

Alembic is used for database migrations.

---

## 13. Monitoring

Vault exposes Prometheus metrics through:

    /metrics

Current metrics include:

    vault_ingestion_duration_seconds
    vault_ingestion_failures_total
    vault_query_latency_seconds

These metrics track document ingestion and RAG query performance.

---

## 14. API Structure

The main API areas are:

    /auth
        POST /signup
        POST /login
        GET  /users/me
        GET  /organizations/{id}

    /documents
        POST /upload
        GET  /{document_id}/status
        GET  /{document_id}/text
        POST /search

    /metrics

---

## 15. Project Structure

    vault/
    │
    ├── app/
    │   ├── api/
    │   │   ├── routes/
    │   │   ├── services/
    │   │   │   └── llm/
    │   │   └── dependencies.py
    │   │
    │   ├── core/
    │   │   ├── config.py
    │   │   ├── security.py
    │   │   ├── metrics.py
    │   │   ├── celery_app.py
    │   │   └── qdrant.py
    │   │
    │   ├── db/
    │   ├── models/
    │   ├── schemas/
    │   └── tasks/
    │
    ├── tests/
    │
    ├── alembic/
    │
    ├── docs/
    │   └── architecture.md
    │
    ├── docker-compose.yml
    ├── Dockerfile
    └── README.md

---

## 16. Testing

The project contains automated tests covering:

- Authentication
- User registration
- Login
- JWT-protected endpoints
- Organization isolation
- Document access isolation
- Document ingestion
- Vector search isolation
- RAG tenant isolation

Tests use FastAPI `TestClient`, pytest fixtures, and mocked services where appropriate.

Run the test suite with:

    pytest

---

## 17. Design Principles

The project follows several core principles:

- Authentication is required for protected resources.
- Users belong to organizations.
- Organization ownership controls document access.
- Vector searches are filtered by organization.
- Passwords are never stored in raw form.
- Document processing is separated from API responsibilities.
- LLM integration is abstracted behind a provider interface.
- Database schema changes are managed through Alembic migrations.
- Application metrics are exposed for monitoring.