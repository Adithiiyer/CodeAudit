import re
from .base_agent import BaseAgent

class CodeQualityAgent(BaseAgent):
    def analyze(self, code: str, language: str) -> dict:
        lines = code.splitlines()
        total_lines = len(lines)

        comment_lines = sum(1 for l in lines if l.strip().startswith(("#", "//")))
        blank_lines = sum(1 for l in lines if not l.strip())
        long_lines = sum(1 for l in lines if len(l) > 120)

        complexity_keywords = [" if ", " for ", " while ", " and ", " or ", " try ", " except "]
        complexity = sum(code.count(k) for k in complexity_keywords)

        bad_names = len(re.findall(r"\b[a-zA-Z]{1,2}\b", code))

        score = 100
        score -= int(complexity * 1.5)
        score -= long_lines * 1
        score -= bad_names * 2

        comment_ratio = comment_lines / max(1, (total_lines - blank_lines))
        if comment_ratio < 0.10:
            score -= 10

        score = max(0, min(100, score))

        issues = []
        if comment_ratio < 0.10: issues.append("Low comment density.")
        if long_lines > 0: issues.append(f"{long_lines} overly long lines (>120 chars).")
        if complexity > 15: issues.append("High cyclomatic complexity.")
        if bad_names > 5: issues.append("Too many single-letter variable names.")

        summary = (
            f"Lines: {total_lines}, Comments: {comment_lines}, "
            f"Long lines: {long_lines}, Complexity: {complexity}."
        )

        return {"score": score, "summary": summary, "issues": issues}
