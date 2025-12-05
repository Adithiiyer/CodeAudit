from .base_agent import BaseAgent

class PerformanceAgent(BaseAgent):
    def analyze(self, code: str, language: str) -> dict:
        loops = code.count("for ") + code.count("while ")
        nested = loops > 5

        score = 100
        score -= loops * 1
        if nested:
            score -= 10

        score = max(0, min(100, score))

        issues = []
        if loops > 10:
            issues.append(f"Too many loops ({loops}).")
        if nested:
            issues.append("Nested loop patterns detected.")

        summary = f"Loop count: {loops}, Nested risk: {nested}"

        return {"score": score, "summary": summary, "issues": issues}
