from agents.base_agent import BaseAgent
from typing import Dict, Any
import json

class CodeReviewAgent(BaseAgent):
    """AI agent for semantic code review"""
    
    def get_system_prompt(self) -> str:
        return """You are an expert code reviewer with deep knowledge of software engineering best practices.

Analyze code for:
1. Code quality and design patterns
2. Best practices and conventions
3. Readability and maintainability
4. Performance considerations
5. Potential bugs and edge cases
6. Documentation quality

Provide constructive, actionable feedback in JSON format with:
{
  "overall_score": <0-100>,
  "issues": [
    {
      "line": <line_number>,
      "severity": "error|warning|info",
      "message": "description of issue",
      "category": "performance|design|style|logic"
    }
  ],
  "suggestions": [
    "actionable improvement suggestion"
  ],
  "positive_aspects": [
    "things done well"
  ]
}

Be specific, provide examples, and focus on teaching."""
    
    def process(self, code: str, static_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Review code semantically using LLM
        """
        # Prepare context from static analysis
        complexity_issues = [c for c in static_analysis.get('complexity', []) if c.get('complexity', 0) > 10]
        syntax_valid = static_analysis.get('syntax_check', {}).get('valid', True)
        mi_score = static_analysis.get('maintainability_index', 65)
        
        context = f"""
Code to review:
```
{code[:3000]}  
```

Static analysis results:
- Syntax valid: {syntax_valid}
- High complexity functions: {len(complexity_issues)}
- Maintainability index: {mi_score:.1f}
- Language: {static_analysis.get('language', 'unknown')}

Please provide a comprehensive code review in JSON format as specified.
"""
        
        response_text = self.call_llm(context)
        
        # Parse JSON response
        try:
            review_results = json.loads(response_text)
            
            # Ensure required fields exist
            if 'overall_score' not in review_results:
                review_results['overall_score'] = 70
            if 'issues' not in review_results:
                review_results['issues'] = []
            if 'suggestions' not in review_results:
                review_results['suggestions'] = []
            if 'positive_aspects' not in review_results:
                review_results['positive_aspects'] = []
            
            return review_results
        
        except json.JSONDecodeError:
            # Fallback if LLM doesn't return valid JSON
            return {
                "overall_score": 70,
                "issues": [],
                "suggestions": [response_text[:500]],
                "positive_aspects": [],
                "error": "Failed to parse LLM response as JSON"
            }
