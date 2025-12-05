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
    all_issues = []

    for name, agent, weight in agents:
        result = agent.analyze(code, language)
        final_score += result["score"] * weight
        summaries.append(f"[{name.upper()}]\n{result['summary']}")
        
        # Format issues with category prefix
        for issue in result["issues"]:
            all_issues.append(f"[{name.upper()}] {issue}")

    # Join issues with newlines for storage
    issues_text = "\n".join(all_issues) if all_issues else "No issues found"
    
    return int(final_score), "\n\n".join(summaries), issues_text