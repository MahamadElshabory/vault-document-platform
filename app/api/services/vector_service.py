from qdrant_client.models import (Distance,FieldCondition,Filter,VectorParams,PointStruct)
from qdrant_client.models import (Filter,FieldCondition,MatchValue)

from app.core.qdrant import qdrant_client
from uuid import uuid4



class VectorService:

    COLLECTION_NAME = "document_chunks"


    def create_collection(self):

        collections = qdrant_client.get_collections()

        existing = [
            collection.name
            for collection in collections.collections
        ]

        if self.COLLECTION_NAME not in existing:

            qdrant_client.create_collection(
                collection_name=self.COLLECTION_NAME,
                vectors_config=VectorParams(
                    size=384,
                    distance=Distance.COSINE
                )
            )


    def store_vector(
        self,
        vector: list,
        document_id: int,
        org_id: int,
        chunk_index: int,
        text: str
    ):

        point = PointStruct(

            id=str(uuid4()),

            vector=vector,

            payload={
                "document_id": document_id,
                "org_id": org_id,
                "chunk_index": chunk_index,
                "text": text
            }
        )


        qdrant_client.upsert(
            collection_name=self.COLLECTION_NAME,
            points=[point]
        )
        
        
   


    def search_vectors(
        self,
        vector: list,
        org_id: int,
        limit: int = 5
    ):

        search_result = qdrant_client.query_points(
            collection_name=self.COLLECTION_NAME,
            query=vector,
            limit=limit,
            query_filter=Filter(
                must=[
                    FieldCondition(
                        key="org_id",
                        match=MatchValue(
                            value=org_id
                        )
                    )
                ]
            )
        )

        return [
        {
            "score": result.score,
            "document_id": result.payload["document_id"],
            "chunk_index": result.payload["chunk_index"],
            "text": result.payload["text"]
        }
        for result in search_result.points
    ]   

        
        
        