from abc import ABC, abstractmethod
from typing import Dict, Any
import openai
import os

class BaseAgent(ABC):
    def __init__(self, model: str = "gpt-4"):
        self.model = model
        openai.api_key = os.getenv("OPENAI_API_KEY")
    
    @abstractmethod
    def get_system_prompt(self) -> str:
        """Return the system prompt for this agent"""
        pass
    
    @abstractmethod
    def process(self, code: str, static_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Process code and return analysis"""
        pass
    
    def call_llm(self, user_message: str) -> str:
        """
        Call OpenAI API with system + user message
        """
        response = openai.ChatCompletion.create(
            model=self.model,
            messages=[
                {"role": "system", "content": self.get_system_prompt()},
                {"role": "user", "content": user_message}
            ],
            temperature=0.3,
            max_tokens=2000
        )
        
        return response.choices[0].message.content