from .storage import write_report
from ..agents.aggregator import run_all_agents

def analyze_file(sub_id, path, language):
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        code = f.read()

    score, summary, issues = run_all_agents(code, language)

    report = f"""
    CodeAudit Report — Submission {sub_id}
    =====================================

    Score: {score}

    Summary:
    {summary}

    Issues:
    {issues}
    """

    write_report(sub_id, report)

    return score, summary, issues
