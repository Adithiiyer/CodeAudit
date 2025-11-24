from agents.base_agent import BaseAgent
from typing import Dict, Any, List
import json

class FeedbackChatAgent(BaseAgent):
    """AI agent for interactive Q&A about code reviews"""
    
    def __init__(self, model: str = "gpt-4o-mini"):
        super().__init__(model)
        self.conversation_history = []
    
    def get_system_prompt(self) -> str:
        return """You are a helpful code review assistant. You have access to:
- The original code that was reviewed
- Static analysis results
- AI-generated review feedback
- Security analysis

Answer questions about:
- Why specific issues were flagged
- How to fix identified problems
- Best practices for the code
- Explanations of scores and metrics
- Detailed code explanations

Be clear, concise, and provide actionable advice with code examples when helpful.
Use markdown formatting for code snippets."""
    
    def chat(
        self, 
        user_question: str, 
        code: str, 
        review_results: Dict[str, Any]
    ) -> str:
        """
        Interactive Q&A about code review results
        """
        # Build context from review results
        context = self._build_context(code, review_results)
        
        # Create full prompt with context
        full_prompt = f"""
Code Review Context:
{context}

User Question: {user_question}

Please provide a helpful answer based on the code review results above.
"""
        
        # Get response from LLM
        response = self._call_with_history(full_prompt)
        
        # Add to conversation history
        self.conversation_history.append({
            "role": "user",
            "content": user_question
        })
        self.conversation_history.append({
            "role": "assistant",
            "content": response
        })
        
        return response
    
    def _build_context(self, code: str, review_results: Dict[str, Any]) -> str:
        """
        Build context string from review results
        """
        context_parts = [
            "Original Code:",
            f"```\n{code[:2000]}\n```",
            "",
            f"Overall Score: {review_results.get('overall_score', 'N/A')}/100",
            f"Quality Score: {review_results.get('quality_score', 'N/A')}/100",
            f"Security Score: {review_results.get('security_score', 'N/A')}/100",
            "",
            "Issues Found:"
        ]
        
        # Add issues from AI review
        ai_review = review_results.get('ai_review', {})
        for issue in ai_review.get('issues', [])[:10]:  # Limit to 10 issues
            line = issue.get('line', 'N/A')
            message = issue.get('message', 'No message')
            context_parts.append(f"- Line {line}: {message}")
        
        # Add security vulnerabilities
        security = review_results.get('security_analysis', {})
        for vuln in security.get('vulnerabilities', [])[:5]:  # Limit to 5
            line = vuln.get('line', 'N/A')
            desc = vuln.get('description', vuln.get('issue', 'No description'))
            context_parts.append(f"- Line {line}: [SECURITY] {desc}")
        
        return "\n".join(context_parts)
    
    def _call_with_history(self, user_message: str) -> str:
        """
        Call LLM with conversation history
        """
        if not self.api_key:
            return "Error: OpenAI API key not configured"
        
        try:
            import openai
            openai.api_key = self.api_key
            
            messages = [
                {"role": "system", "content": self.get_system_prompt()}
            ]
            
            # Add conversation history (limit to last 10 exchanges)
            messages.extend(self.conversation_history[-10:])
            
            # Add current message
            messages.append({"role": "user", "content": user_message})
            
            response = openai.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.3,
                max_tokens=1000
            )
            
            return response.choices[0].message.content
        
        except Exception as e:
            return f"Error: {str(e)}"
    
    def reset_conversation(self):
        """Clear conversation history"""
        self.conversation_history = []
