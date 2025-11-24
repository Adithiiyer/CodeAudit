from abc import ABC, abstractmethod
from typing import Dict, Any
import os
from dotenv import load_dotenv

load_dotenv()

class BaseAgent(ABC):
    """Base class for all AI agents"""
    
    def __init__(self, model: str = "gpt-4o-mini"):
        self.model = model
        self.api_key = os.getenv("OPENAI_API_KEY")
        
        if not self.api_key:
            print("Warning: OPENAI_API_KEY not set. AI agents will not work.")
    
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
        if not self.api_key:
            return '{"error": "OpenAI API key not configured"}'
        
        try:
            import openai
            openai.api_key = self.api_key
            
            response = openai.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.get_system_prompt()},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.3,
                max_tokens=2000
            )
            
            return response.choices[0].message.content
        
        except Exception as e:
            print(f"Error calling LLM: {e}")
            return f'{{"error": "LLM call failed: {str(e)}"}}'
