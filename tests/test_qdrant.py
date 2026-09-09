import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from app.api.services.embedding_service import EmbeddingService
from app.api.services.vector_service import VectorService


embedding_service = EmbeddingService()
vector_service = VectorService()


text = "Employees receive 30 days annual leave"


# 1. Create embedding
vector = embedding_service.create_embedding(text)

print("Vector size:", len(vector))


# 2. Create collection
vector_service.create_collection()


# 3. Store vector
vector_service.store_vector(
    vector=vector,
    document_id=1,
    org_id=1,
    chunk_index=0,
    text=text
)


print("Vector stored successfully")