from static_analyzers.python_analyzer import PythonAnalyzer
from static_analyzers.javascript_analyzer import JavaScriptAnalyzer
from static_analyzers.java_analyzer import JavaAnalyzer
from typing import Dict, Any

class LanguageRouter:
    """Routes code to appropriate analyzer based on language"""
    
    def __init__(self):
        self.analyzers = {
            'python': PythonAnalyzer(),
            'javascript': JavaScriptAnalyzer(),
            'typescript': JavaScriptAnalyzer(),
            'java': JavaAnalyzer()
        }
    
    def detect_language(self, file_path: str, code: str = None) -> str:
        """
        Detect programming language from file extension or content
        """
        extension_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.jsx': 'javascript',
            '.ts': 'typescript',
            '.tsx': 'typescript',
            '.java': 'java',
            '.cpp': 'cpp',
            '.c': 'c',
            '.go': 'go',
            '.rb': 'ruby',
            '.php': 'php'
        }
        
        # Get extension
        if '.' in file_path:
            ext = '.' + file_path.split('.')[-1]
            language = extension_map.get(ext.lower(), 'unknown')
        else:
            language = 'unknown'
        
        # Try to detect from content if unknown
        if language == 'unknown' and code:
            language = self._detect_from_content(code)
        
        return language
    
    def _detect_from_content(self, code: str) -> str:
        """
        Attempt to detect language from code content
        """
        code_lower = code.lower()
        
        # Simple heuristics
        if 'def ' in code and 'import ' in code:
            return 'python'
        elif 'function ' in code or 'const ' in code or 'let ' in code:
            return 'javascript'
        elif 'public class ' in code or 'public static void main' in code:
            return 'java'
        
        return 'unknown'
    
    def get_analyzer(self, language: str):
        """
        Get the appropriate analyzer for a language
        """
        return self.analyzers.get(language)
    
    def analyze(self, code: str, file_path: str, language: str = None) -> Dict[str, Any]:
        """
        Route to appropriate analyzer based on language
        """
        if not language:
            language = self.detect_language(file_path, code)
        
        analyzer = self.get_analyzer(language)
        
        if not analyzer:
            return {
                "error": f"No analyzer available for language: {language}",
                "language": language,
                "syntax_check": {"valid": True, "errors": []},
                "complexity": [],
                "maintainability_index": 65.0,
                "security_issues": []
            }
        
        results = analyzer.analyze(code, file_path)
        results['language'] = language
        
        return results
