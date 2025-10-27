import ast
import pylint.lint
from pylint.reporters.text import TextReporter
from io import StringIO
from radon.complexity import cc_visit
from radon.metrics import mi_visit
import bandit
from bandit.core import manager as bandit_manager

class PythonAnalyzer:
    def analyze(self, code: str, file_path: str) -> dict:
        """
        Run comprehensive Python analysis
        """
        results = {
            "syntax_check": self._check_syntax(code),
            "pylint_results": self._run_pylint(file_path),
            "complexity": self._calculate_complexity(code),
            "maintainability_index": self._calculate_mi(code),
            "security_issues": self._run_bandit(file_path)
        }
        
        return results
    
    def _check_syntax(self, code: str) -> dict:
        try:
            ast.parse(code)
            return {"valid": True, "errors": []}
        except SyntaxError as e:
            return {
                "valid": False,
                "errors": [{
                    "line": e.lineno,
                    "message": e.msg,
                    "text": e.text
                }]
            }
    
    def _run_pylint(self, file_path: str) -> dict:
        """
        Run pylint and capture results
        """
        pylint_output = StringIO()
        reporter = TextReporter(pylint_output)
        
        pylint.lint.Run(
            [file_path, '--output-format=json'],
            reporter=reporter,
            exit=False
        )
        
        return {"report": pylint_output.getvalue()}
    
    def _calculate_complexity(self, code: str) -> list:
        """
        Calculate cyclomatic complexity
        """
        complexity_results = cc_visit(code)
        return [
            {
                "name": item.name,
                "complexity": item.complexity,
                "line": item.lineno
            }
            for item in complexity_results
        ]
    
    def _calculate_mi(self, code: str) -> float:
        """
        Calculate maintainability index (0-100, higher is better)
        """
        mi_results = mi_visit(code, multi=True)
        return mi_results
    
    def _run_bandit(self, file_path: str) -> list:
        """
        Run security analysis with Bandit
        """
        b_mgr = bandit_manager.BanditManager(
            bandit.core.config.BanditConfig(),
            'file'
        )
        b_mgr.discover_files([file_path])
        b_mgr.run_tests()
        
        issues = []
        for result in b_mgr.results:
            issues.append({
                "severity": result.severity,
                "confidence": result.confidence,
                "issue": result.text,
                "line": result.lineno
            })
        
        return issues