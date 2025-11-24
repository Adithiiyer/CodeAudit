import ast
import subprocess
import tempfile
import os
from io import StringIO
from typing import Dict, List, Any
import json

class PythonAnalyzer:
    """Comprehensive Python code analyzer"""
    
    def analyze(self, code: str, file_path: str) -> Dict[str, Any]:
        """
        Run comprehensive Python analysis
        """
        results = {
            "language": "python",
            "syntax_check": self._check_syntax(code),
            "pylint_results": self._run_pylint(code, file_path),
            "complexity": self._calculate_complexity(code),
            "maintainability_index": self._calculate_mi(code),
            "security_issues": self._run_bandit(code, file_path)
        }
        
        return results
    
    def _check_syntax(self, code: str) -> Dict[str, Any]:
        """Check Python syntax"""
        try:
            ast.parse(code)
            return {"valid": True, "errors": []}
        except SyntaxError as e:
            return {
                "valid": False,
                "errors": [{
                    "line": e.lineno,
                    "offset": e.offset,
                    "message": e.msg,
                    "text": e.text.strip() if e.text else ""
                }]
            }
    
    def _run_pylint(self, code: str, file_path: str) -> Dict[str, Any]:
        """
        Run pylint and capture results
        """
        try:
            # Create temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(code)
                temp_path = f.name
            
            # Run pylint
            result = subprocess.run(
                ['pylint', '--output-format=json', '--disable=C0114,C0115,C0116', temp_path],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            os.unlink(temp_path)
            
            # Parse JSON output
            if result.stdout:
                issues = json.loads(result.stdout)
                return {
                    "issues": issues,
                    "total_issues": len(issues)
                }
            
            return {"issues": [], "total_issues": 0}
            
        except subprocess.TimeoutExpired:
            return {"issues": [], "error": "Pylint timeout"}
        except Exception as e:
            return {"issues": [], "error": str(e)}
    
    def _calculate_complexity(self, code: str) -> List[Dict[str, Any]]:
        """
        Calculate cyclomatic complexity using radon
        """
        try:
            from radon.complexity import cc_visit
            
            complexity_results = cc_visit(code)
            return [
                {
                    "name": item.name,
                    "complexity": item.complexity,
                    "line": item.lineno,
                    "rank": item.letter
                }
                for item in complexity_results
            ]
        except Exception as e:
            return []
    
    def _calculate_mi(self, code: str) -> float:
        """
        Calculate maintainability index (0-100, higher is better)
        """
        try:
            from radon.metrics import mi_visit
            
            mi_result = mi_visit(code, multi=True)
            # Average MI if multiple values
            if isinstance(mi_result, (int, float)):
                return float(mi_result)
            return 65.0  # Default
        except Exception as e:
            return 65.0
    
    def _run_bandit(self, code: str, file_path: str) -> List[Dict[str, Any]]:
        """
        Run security analysis with Bandit
        """
        try:
            # Create temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(code)
                temp_path = f.name
            
            # Run bandit
            result = subprocess.run(
                ['bandit', '-f', 'json', temp_path],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            os.unlink(temp_path)
            
            # Parse JSON output
            if result.stdout:
                bandit_output = json.loads(result.stdout)
                issues = []
                for result_item in bandit_output.get('results', []):
                    issues.append({
                        "severity": result_item.get('issue_severity'),
                        "confidence": result_item.get('issue_confidence'),
                        "issue": result_item.get('issue_text'),
                        "line": result_item.get('line_number'),
                        "test_id": result_item.get('test_id'),
                        "more_info": result_item.get('more_info')
                    })
                return issues
            
            return []
            
        except subprocess.TimeoutExpired:
            return []
        except Exception as e:
            return []
