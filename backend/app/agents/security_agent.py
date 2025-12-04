from .base_agent import BaseAgent

class SecurityAgent(BaseAgent):
    def analyze(self, code: str, language: str) -> dict:
        insecure = {
            "eval(": "Use of eval() is dangerous.",
            "exec(": "exec() can allow remote code execution.",
            "pickle.loads": "Untrusted pickle loading detected.",
            "yaml.load(": "Unsafe YAML load; use safe_load.",
            "os.system(": "Shell execution detected.",
            "subprocess.Popen(": "Possible command injection."
        }

        findings = [msg for pattern, msg in insecure.items() if pattern in code]

        score = 100 - len(findings) * 15
        score = max(0, min(100, score))

        summary = f"Security issues: {len(findings)}"

        return {"score": score, "summary": summary, "issues": findings}
