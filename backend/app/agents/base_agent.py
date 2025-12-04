from abc import ABC, abstractmethod

class BaseAgent(ABC):
    @abstractmethod
    def analyze(self, code: str, language: str) -> dict:
        pass
