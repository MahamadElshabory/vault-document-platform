from ollama import Client

from app.api.services.llm.base import LLMProvider
from app.core.config import settings


class OllamaProvider(LLMProvider):

    def __init__(self):

        self.client = Client(
            host=settings.ollama_host
        )

        self.model = settings.ollama_model


    def generate_answer(
        self,
        question: str,
        context: list[str]
    ) -> str:

        context_text = "\n\n".join(context)

        prompt = f"""
You are a document question-answering assistant.

Answer the user's question using ONLY the provided context.

Do not use outside knowledge.

If the answer cannot be found in the provided context,
say:

"I couldn't find the answer in the provided documents."

Context:
{context_text}

Question:
{question}
"""

        response = self.client.chat(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        return response["message"]["content"]