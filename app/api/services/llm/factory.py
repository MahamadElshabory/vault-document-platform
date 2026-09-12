from app.api.services.llm.base import LLMProvider
from app.api.services.llm.ollama_provider import OllamaProvider


def get_llm_provider() -> LLMProvider:

    return OllamaProvider()