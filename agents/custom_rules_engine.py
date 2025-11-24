import re
import ast
from typing import List, Dict, Any

class CustomRulesEngine:
    """Engine for evaluating custom user-defined rules"""
    
    def __init__(self, rules: List[Dict[str, Any]]):
        self.rules = rules
    
    def check_rules(self, code: str, language: str, file_path: str) -> List[Dict[str, Any]]:
        """
        Check code against custom rules
        """
        violations = []
        
        for rule in self.rules:
            if not rule.get('enabled', True):
                continue
            
            # Check if rule applies to this language
            rule_lang = rule.get('language', 'all')
            if rule_lang not in ['all', language]:
                continue
            
            rule_type = rule.get('rule_type', 'pattern')
            
            try:
                if rule_type == 'pattern':
                    violations.extend(self._check_pattern_rule(code, rule))
                elif rule_type == 'naming':
                    violations.extend(self._check_naming_rule(code, rule, language))
                elif rule_type == 'complexity':
                    violations.extend(self._check_complexity_rule(code, rule, language))
                elif rule_type == 'forbidden':
                    violations.extend(self._check_forbidden_rule(code, rule))
            except Exception as e:
                print(f"Error checking rule {rule.get('name')}: {e}")
        
        return violations
    
    def _check_pattern_rule(self, code: str, rule: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Check for regex pattern violations
        """
        violations = []
        pattern = rule.get('pattern', '')
        
        if not pattern:
            return violations
        
        try:
            regex = re.compile(pattern)
            
            for line_num, line in enumerate(code.split('\n'), 1):
                if regex.search(line):
                    violations.append({
                        'rule_name': rule.get('name', 'Custom Rule'),
                        'line': line_num,
                        'severity': rule.get('severity', 'warning'),
                        'message': rule.get('message', 'Pattern matched'),
                        'matched_text': line.strip()[:100]
                    })
        except re.error as e:
            print(f"Invalid regex pattern in rule {rule.get('name')}: {e}")
        
        return violations
    
    def _check_naming_rule(self, code: str, rule: Dict[str, Any], language: str) -> List[Dict[str, Any]]:
        """
        Check naming conventions
        """
        violations = []
        
        if language == 'python':
            try:
                tree = ast.parse(code)
                pattern = rule.get('pattern', '')
                
                if not pattern:
                    return violations
                
                regex = re.compile(pattern)
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        # Check function name
                        if not regex.match(node.name):
                            violations.append({
                                'rule_name': rule.get('name', 'Naming Rule'),
                                'line': node.lineno,
                                'severity': rule.get('severity', 'warning'),
                                'message': f"{rule.get('message', 'Naming violation')}: '{node.name}'",
                                'matched_text': node.name
                            })
                    
                    elif isinstance(node, ast.ClassDef):
                        # Check class name
                        if not regex.match(node.name):
                            violations.append({
                                'rule_name': rule.get('name', 'Naming Rule'),
                                'line': node.lineno,
                                'severity': rule.get('severity', 'warning'),
                                'message': f"{rule.get('message', 'Naming violation')}: '{node.name}'",
                                'matched_text': node.name
                            })
            
            except SyntaxError:
                pass  # Already handled in syntax check
        
        return violations
    
    def _check_complexity_rule(self, code: str, rule: Dict[str, Any], language: str) -> List[Dict[str, Any]]:
        """
        Check complexity thresholds
        """
        violations = []
        
        if language == 'python':
            try:
                from radon.complexity import cc_visit
                
                config = rule.get('config', {})
                max_complexity = config.get('max_complexity', 10)
                
                complexity_results = cc_visit(code)
                
                for result in complexity_results:
                    if result.complexity > max_complexity:
                        violations.append({
                            'rule_name': rule.get('name', 'Complexity Rule'),
                            'line': result.lineno,
                            'severity': rule.get('severity', 'warning'),
                            'message': f"{rule.get('message', 'High complexity')}: {result.complexity} exceeds {max_complexity}",
                            'matched_text': result.name
                        })
            except Exception as e:
                print(f"Error checking complexity: {e}")
        
        return violations
    
    def _check_forbidden_rule(self, code: str, rule: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Check for forbidden functions/imports
        """
        violations = []
        
        config = rule.get('config', {})
        forbidden_items = config.get('forbidden_items', [])
        
        for line_num, line in enumerate(code.split('\n'), 1):
            for forbidden in forbidden_items:
                if forbidden in line:
                    violations.append({
                        'rule_name': rule.get('name', 'Forbidden Rule'),
                        'line': line_num,
                        'severity': rule.get('severity', 'error'),
                        'message': f"{rule.get('message', 'Forbidden item found')}: '{forbidden}'",
                        'matched_text': line.strip()[:100]
                    })
        
        return violations
