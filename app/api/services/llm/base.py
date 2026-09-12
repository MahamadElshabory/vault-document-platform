from abc import ABC, abstractmethod


class LLMProvider(ABC):

    @abstractmethod
    def generate_answer(
        self,
        question: str,
        context: list[str]
    ) -> str:
        pass