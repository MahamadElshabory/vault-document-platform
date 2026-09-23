# Vault

Vault is a secure, multi-tenant document intelligence platform built with Python and FastAPI.

Users can upload PDF documents, process their content into searchable vector representations, and ask questions using a Retrieval-Augmented Generation (RAG) pipeline.

## Features

- JWT authentication
- Organization-based multi-tenancy
- Secure document access
- PDF text extraction and OCR
- Text chunking
- Vector embeddings
- Qdrant vector search
- Organization-scoped RAG search
- Ollama-powered question answering
- Redis and Celery background processing
- Prometheus metrics
- Automated tests for authentication, tenancy, ingestion, and RAG isolation

## Architecture

```text
Client
  |
  v
FastAPI
  |
  +-------------------+
  |                   |
  v                   v
Authentication     Documents
  |                   |
  |                   +--> PDF Extraction
  |                   +--> OCR
  |                   +--> Chunking
  |                   +--> Embeddings
  |                   +--> Qdrant
  |
  +--> PostgreSQL

RAG Search
  |
  +--> Embedding
  +--> Organization-scoped Qdrant Search
  +--> Ollama
  +--> Answer


## Technology Stack

| Area            | Technology                          |
| --------------- | ----------------------------------- |
| Backend         | Python, FastAPI                     |
| Database        | PostgreSQL                          |
| ORM             | SQLModel, SQLAlchemy                |
| Migrations      | Alembic                             |
| Authentication  | JWT, PyJWT, pwdlib                  |
| PDF Processing  | PyMuPDF, pypdf, pytesseract, Pillow |
| Embeddings      | Sentence Transformers               |
| Vector Database | Qdrant                              |
| LLM             | Ollama                              |
| Task Queue      | Celery, Redis                       |
| Monitoring      | Prometheus                          |
| Testing         | pytest, FastAPI TestClient          |
| Containers      | Docker, Docker Compose              |


## RAG Pipeline

Vault uses Retrieval-Augmented Generation to answer questions from uploaded documents.

PDF
 |
 v
Text Extraction / OCR
 |
 v
Text Chunking
 |
 v
Embeddings
 |
 v
Qdrant
 |
 +------ User Question
          |
          v
       Embedding
          |
          v
   Organization-scoped
      Vector Search
          |
          v
       Ollama
          |
          v
        Answer


The system retrieves relevant document chunks belonging to the user's organization and provides them as context to the LLM.

# Authentication & Multi-Tenancy

Each user belongs to an organization.

Authentication is handled using JWT access tokens.

Document and organization access is restricted by the authenticated user's org_id, preventing users from accessing another organization's data.

# API

## Authentication

| Method | Endpoint                   | Purpose                        |
| ------ | -------------------------- | ------------------------------ |
| POST   | `/auth/signup`             | Create a user and organization |
| POST   | `/auth/login`              | Authenticate a user            |
| GET    | `/auth/users/me`           | Get the current user           |
| GET    | `/auth/organizations/{id}` | Verify organization access     |


## Documents

| Method | Endpoint                 | Purpose                                 |
| ------ | ------------------------ | --------------------------------------- |
| POST   | `/documents/upload`      | Upload and process a PDF                |
| GET    | `/documents/{id}/status` | Get document processing status          |
| GET    | `/documents/{id}/text`   | Retrieve extracted document chunks      |
| POST   | `/documents/search`      | Search documents and generate an answer |


# Running the Project

Create a .env file with the required configuration:

    DATABASE_URL=postgresql+psycopg://postgres:password@postgres:5432/vault
    REDIS_URL=redis://redis:6379/0

    JWT_SECRET_KEY=your-secret-key

    OLLAMA_MODEL=gemma2:2b

Start the services:

    docker compose up -d

The API will be available at:

    http://localhost:8000

FastAPI documentation:

    http://localhost:8000/docs

# Testing

Run the test suite with:

    pytest

The test suite covers:

    User registration and login
    JWT authentication
    Organization isolation
    Document access control
    Document ingestion
    Vector search isolation
    RAG tenant isolation

# Project Structure

vault/
├── app/
│   ├── api/
│   │   ├── routes/
│   │   ├── services/
│   │   └── dependencies.py
│   ├── core/
│   ├── db/
│   ├── models/
│   ├── schemas/
│   └── tasks/
│
├── tests/
├── alembic/
├── uploads/
├── docker-compose.yml
├── Dockerfile
└── README.md

# Security

Vault is designed around organization-level data isolation and authenticated access.

Passwords are stored as hashes, JWTs are used for authentication, and document/vector access is restricted by organization ownership.


### One important change

I intentionally **did not include** the huge Technology Stack explanations, repeated project descriptions, ticket history, or long architecture explanations.

This version gives someone:

**What is it → What does it do → How is it built → How does RAG work → How is security handled → API → Run → Test.**

That's enough for VLT-503 without making the README overwhelming.