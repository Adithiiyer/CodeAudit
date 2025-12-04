from .quality_agent import CodeQualityAgent
from .security_agent import SecurityAgent
from .performance_agent import PerformanceAgent

def run_all_agents(code: str, language: str):
    agents = [
        ("quality", CodeQualityAgent(), 0.5),
        ("security", SecurityAgent(), 0.3),
        ("performance", PerformanceAgent(), 0.2)
    ]

    final_score = 0
    summaries = []
    issues = []

    for name, agent, weight in agents:
        result = agent.analyze(code, language)
        final_score += result["score"] * weight
        summaries.append(f"[{name.upper()}]\n{result['summary']}")
        issues.extend(result["issues"])

    return int(final_score), "\n\n".join(summaries), "\n".join(issues)
