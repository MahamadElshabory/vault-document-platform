# Vault — Document RAG Backend

Vault is a multi-tenant document question-answering backend built with Python and FastAPI.

Users can upload PDF documents, have them processed into searchable vector representations, and ask questions about their documents using a Retrieval-Augmented Generation (RAG) pipeline.

## Features

- User signup and authentication
- JWT-based authentication
- Organization-based multi-tenancy
- PDF document upload
- PDF text extraction
- Text chunking
- Vector embeddings
- Qdrant vector storage
- Organization-scoped vector search
- RAG-based question answering
- Ollama LLM integration
- Document processing status
- Prometheus metrics
- Ingestion duration monitoring
- Ingestion failure monitoring
- RAG query latency monitoring
- Automated tenancy and ingestion tests

## Tech Stack

### Backend

- Python
- FastAPI
- SQLModel
- PostgreSQL
- Alembic

### Authentication

- JWT
- pwdlib

### Document Processing

- PyMuPDF
- Text chunking
- Embedding model

### Vector Search

- Qdrant

### LLM

- Ollama

### Background Processing

- Redis
- Celery

### Monitoring

- Prometheus

### Testing

- pytest
- FastAPI TestClient
- Mocked embedding services

## Architecture

The current application follows a service-oriented backend structure.

```text
Client
  │
  ▼
FastAPI
  │
  ├── Authentication
  │
  ├── Document API
  │      │
  │      ├── PDF extraction
  │      ├── Chunking
  │      ├── Embeddings
  │      └── Vector storage
  │
  ├── RAG Search
  │      │
  │      ├── Query embedding
  │      ├── Qdrant search
  │      └── LLM generation
  │
  └── Metrics
         │
         ▼
      Prometheus
