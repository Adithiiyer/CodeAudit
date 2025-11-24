import subprocess
import json
import tempfile
import os
from typing import Dict, List, Any

class JavaScriptAnalyzer:
    """Comprehensive JavaScript/TypeScript code analyzer"""
    
    def analyze(self, code: str, file_path: str) -> Dict[str, Any]:
        """
        Run comprehensive JavaScript analysis
        """
        results = {
            "language": "javascript",
            "syntax_check": self._check_syntax(code),
            "eslint_results": self._run_eslint(code, file_path),
            "complexity": []  # Can add complexity analysis later
        }
        
        return results
    
    def _check_syntax(self, code: str) -> Dict[str, Any]:
        """
        Check JavaScript syntax using Node.js
        """
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as f:
                f.write(code)
                temp_path = f.name
            
            # Try to parse with Node
            result = subprocess.run(
                ['node', '--check', temp_path],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            os.unlink(temp_path)
            
            if result.returncode == 0:
                return {"valid": True, "errors": []}
            else:
                return {
                    "valid": False,
                    "errors": [{"message": result.stderr}]
                }
        
        except FileNotFoundError:
            return {"valid": True, "errors": [], "warning": "Node.js not installed"}
        except Exception as e:
            return {"valid": False, "errors": [{"message": str(e)}]}
    
    def _run_eslint(self, code: str, file_path: str) -> Dict[str, Any]:
        """
        Run ESLint on JavaScript code
        Note: Requires ESLint to be installed globally or in project
        """
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as f:
                f.write(code)
                temp_path = f.name
            
            # Create a minimal .eslintrc.json
            eslint_config = {
                "env": {
                    "browser": True,
                    "es2021": True,
                    "node": True
                },
                "extends": "eslint:recommended",
                "parserOptions": {
                    "ecmaVersion": 12,
                    "sourceType": "module"
                },
                "rules": {}
            }
            
            config_path = temp_path + '.eslintrc.json'
            with open(config_path, 'w') as f:
                json.dump(eslint_config, f)
            
            # Run ESLint with JSON output
            result = subprocess.run(
                ['eslint', '--format=json', '--config', config_path, temp_path],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            os.unlink(temp_path)
            os.unlink(config_path)
            
            # Parse ESLint JSON output
            if result.stdout:
                eslint_output = json.loads(result.stdout)
                if eslint_output:
                    return {
                        "issues": eslint_output[0].get('messages', []),
                        "total_issues": len(eslint_output[0].get('messages', []))
                    }
            
            return {"issues": [], "total_issues": 0}
        
        except FileNotFoundError:
            return {"issues": [], "warning": "ESLint not installed"}
        except subprocess.TimeoutExpired:
            return {"issues": [], "error": "ESLint timeout"}
        except Exception as e:
            return {"issues": [], "error": str(e)}
