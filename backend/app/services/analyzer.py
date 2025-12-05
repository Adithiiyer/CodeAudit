from app.services.storage import write_report
from app.services.llm_service import generate_llm_feedback
from app.agents.aggregator import run_all_agents


def analyze_file(sub_id, path, language):
    with open(path, "r", encoding="utf-8") as f:
        code = f.read()

    score, summary, issues = run_all_agents(code, language)

    llm_json = generate_llm_feedback(code, summary, issues, score)

    report = f"""
CodeAudit Report — Submission {sub_id}

Score: {score}

Summary:
{summary}

Issues:
{issues}

LLM Analysis:
{llm_json}
"""

    write_report(sub_id, report)

    return score, summary, issues, llm_json
