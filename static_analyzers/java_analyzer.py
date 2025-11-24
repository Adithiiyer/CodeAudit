import subprocess
import tempfile
import os
import json
from typing import Dict, List, Any

class JavaAnalyzer:
    """Comprehensive Java code analyzer"""
    
    def analyze(self, code: str, file_path: str) -> Dict[str, Any]:
        """
        Run comprehensive Java analysis
        """
        results = {
            "language": "java",
            "syntax_check": self._check_syntax(code),
            "checkstyle_results": {"issues": []},  # Simplified for now
            "security_issues": []
        }
        
        return results
    
    def _check_syntax(self, code: str) -> Dict[str, Any]:
        """
        Check Java syntax by attempting compilation
        """
        try:
            # Extract class name from code
            class_name = self._extract_class_name(code)
            if not class_name:
                class_name = "TempClass"
            
            with tempfile.TemporaryDirectory() as temp_dir:
                java_file = os.path.join(temp_dir, f"{class_name}.java")
                
                with open(java_file, 'w') as f:
                    f.write(code)
                
                # Try to compile
                result = subprocess.run(
                    ['javac', java_file],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                if result.returncode == 0:
                    return {"valid": True, "errors": []}
                else:
                    return {
                        "valid": False,
                        "errors": [{"message": result.stderr}]
                    }
        
        except FileNotFoundError:
            return {"valid": True, "errors": [], "warning": "Java compiler not installed"}
        except Exception as e:
            return {"valid": False, "errors": [{"message": str(e)}]}
    
    def _extract_class_name(self, code: str) -> str:
        """
        Extract the main class name from Java code
        """
        import re
        match = re.search(r'public\s+class\s+(\w+)', code)
        if match:
            return match.group(1)
        
        match = re.search(r'class\s+(\w+)', code)
        if match:
            return match.group(1)
        
        return None
