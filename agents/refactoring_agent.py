from agents.base_agent import BaseAgent
from typing import Dict, Any
import json

class RefactoringAgent(BaseAgent):
    """AI agent for suggesting code refactoring"""
    
    def get_system_prompt(self) -> str:
        return """You are a code refactoring expert who helps improve code structure and quality.

Analyze code for refactoring opportunities:
1. Extract methods/functions
2. Reduce complexity
3. Remove code duplication
4. Improve naming
5. Simplify logic
6. Apply design patterns
7. Optimize performance
8. Improve error handling

Return suggestions in JSON format:
{
  "refactoring_score": <0-100>,
  "suggestions": [
    {
      "type": "extract-method|simplify|rename|pattern|performance",
      "priority": "high|medium|low",
      "description": "what to refactor",
      "before": "code snippet if applicable",
      "after": "improved version",
      "rationale": "why this improves the code"
    }
  ],
  "summary": "overall refactoring recommendations"
}

Provide practical, implementable suggestions with code examples."""
    
    def process(self, code: str, static_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate refactoring suggestions
        """
        complexity = static_analysis.get('complexity', [])
        high_complexity = [c for c in complexity if c.get('complexity', 0) > 10]
        
        context = f"""
Code to refactor:
```
{code[:3000]}
```

Complexity analysis:
- Functions with high complexity: {len(high_complexity)}
{json.dumps(high_complexity[:3], indent=2) if high_complexity else "None"}

Language: {static_analysis.get('language', 'unknown')}
Maintainability Index: {static_analysis.get('maintainability_index', 65):.1f}

Suggest practical refactorings to improve this code. Return JSON format.
"""
        
        response_text = self.call_llm(context)
        
        try:
            refactoring_results = json.loads(response_text)
            
            # Ensure required fields
            if 'refactoring_score' not in refactoring_results:
                refactoring_results['refactoring_score'] = 70
            
            if 'suggestions' not in refactoring_results:
                refactoring_results['suggestions'] = []
            
            if 'summary' not in refactoring_results:
                refactoring_results['summary'] = "No major refactorings needed"
            
            return refactoring_results
        
        except json.JSONDecodeError:
            return {
                "refactoring_score": 70,
                "suggestions": [],
                "summary": response_text[:500],
                "error": "Failed to parse LLM response as JSON"
            }
