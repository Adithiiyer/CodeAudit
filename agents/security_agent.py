from agents.base_agent import BaseAgent
from typing import Dict, Any
import json

class SecurityAgent(BaseAgent):
    """AI agent for security analysis"""
    
    def get_system_prompt(self) -> str:
        return """You are a security expert specializing in code security analysis.

Analyze code for:
1. SQL injection vulnerabilities
2. XSS and CSRF risks
3. Insecure authentication/authorization
4. Hardcoded credentials or secrets
5. Unsafe deserialization
6. Path traversal vulnerabilities
7. Insecure dependencies
8. Data exposure risks
9. Injection attacks
10. Cryptographic issues

Return findings in JSON format:
{
  "security_score": <0-100, higher is safer>,
  "vulnerabilities": [
    {
      "severity": "critical|high|medium|low",
      "category": "injection|crypto|auth|data-exposure|etc",
      "description": "clear explanation",
      "line": <line_number if applicable>,
      "recommendation": "how to fix"
    }
  ],
  "recommendations": [
    "general security improvements"
  ]
}

Be thorough but avoid false positives. Explain the actual risk."""
    
    def process(self, code: str, static_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze code for security vulnerabilities
        """
        bandit_issues = static_analysis.get('security_issues', [])
        language = static_analysis.get('language', 'unknown')
        
        context = f"""
Code to analyze:
```
{code[:3000]}
```

Language: {language}

Automated security scan (Bandit) found {len(bandit_issues)} potential issues:
{json.dumps(bandit_issues[:5], indent=2)}

Perform a comprehensive security assessment and return results in JSON format.
"""
        
        response_text = self.call_llm(context)
        
        try:
            security_results = json.loads(response_text)
            
            # Ensure required fields
            if 'security_score' not in security_results:
                # Calculate score based on vulnerabilities
                vulns = security_results.get('vulnerabilities', [])
                critical = sum(1 for v in vulns if v.get('severity') == 'critical')
                high = sum(1 for v in vulns if v.get('severity') == 'high')
                
                # Deduct points for vulnerabilities
                security_results['security_score'] = max(0, 100 - (critical * 20) - (high * 10))
            
            if 'vulnerabilities' not in security_results:
                security_results['vulnerabilities'] = bandit_issues
            
            if 'recommendations' not in security_results:
                security_results['recommendations'] = []
            
            return security_results
        
        except json.JSONDecodeError:
            return {
                "security_score": 75,
                "vulnerabilities": bandit_issues,
                "recommendations": [response_text[:500]],
                "error": "Failed to parse LLM response as JSON"
            }
