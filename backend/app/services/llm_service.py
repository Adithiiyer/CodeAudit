import os
from groq import Groq
from app.config import GROQ_API_KEY

client = Groq(api_key=GROQ_API_KEY)

# Correct model name
MODEL = "llama-3.1-8b-instant"

def generate_llm_feedback(code, summary, issues, score):
    prompt = f"""
You are a senior software engineer. Analyze this code deeply.

CODE:
{code}

SUMMARY:
{summary}

ISSUES:
{issues}

STATIC SCORE: {score}

Return ONLY valid JSON:
{{
  "analysis": "...",
  "suggestions": "...",
  "importance": "..."
}}
"""

    response = client.chat.completions.create(
        model=MODEL,
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}],
    )

    # FIXED: Groq SDK returns ChatCompletionMessage, not a dict
    return response.choices[0].message.content
