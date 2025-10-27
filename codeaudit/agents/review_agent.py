from agents.base_agent import BaseAgent
from typing import Dict, Any
import json

class CodeReviewAgent(BaseAgent):
    def get_system_prompt(self) -> str:
        return """You are an expert code reviewer. Analyze code for:
        
        1. Code quality and best practices
        2. Design patterns and architecture
        3. Readability and maintainability
        4. Performance considerations
        5. Edge cases and potential bugs
        
        Provide constructive, actionable feedback in JSON format with:
        - overall_score (0-100)
        - issues (list of concerns with line numbers)
        - suggestions (list of improvements)
        - positive_aspects (things done well)
        """
    
    def process(self, code: str, static_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Review code semantically using LLM
        """
        # Prepare context from static analysis
        context = f"""
        Code to review:
```
        {code}
```
        
        Static analysis results:
        - Syntax valid: {static_analysis.get('syntax_check', {}).get('valid', 'Unknown')}
        - Complexity issues: {len([c for c in static_analysis.get('complexity', []) if c['complexity'] > 10])}
        - Maintainability index: {static_analysis.get('maintainability_index', 'N/A')}
        
        Please provide a comprehensive code review.
        """
        
        response_text = self.call_llm(context)
        
        # Parse JSON response
        try:
            review_results = json.loads(response_text)
        except json.JSONDecodeError:
            # Fallback if LLM doesn't return valid JSON
            review_results = {
                "overall_score": 70,
                "issues": [],
                "suggestions": [response_text],
                "positive_aspects": []
            }
        
        return review_results