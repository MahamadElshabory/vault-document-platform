from sentence_transformers import SentenceTransformer


class EmbeddingService:

    def __init__(self):
        self.model = None


    def get_model(self):

        if self.model is None:
            self.model = SentenceTransformer(
                "all-MiniLM-L6-v2"
            )

        return self.model


    def create_embedding(self, text: str):

        model = self.get_model()

        vector = model.encode(text)

        return vector.tolist()