from Config.config import client, MODEL_NAME

def repair_code(
    original_code,
    error_message
):
    prompt = f"""
You are a strict Python code repair agent.

IMPORTANT RULES:

1. Preserve original task and logic.
2. NEVER change API URL.
3. NEVER invent new URLs.
4. NEVER change user inputs.
5. ONLY fix Python code issues.
6. If failure is caused by invalid external input,
   explain that code cannot repair it.
7. Return executable Python code only.
8. No markdown.
9. No explanations.

ORIGINAL CODE:

{original_code}

ERROR:

{error_message}

Return repaired code.
"""

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt
    )

    code = response.text
    code = code.replace(
        "```python",
        ""
    )
    code = code.replace(
        "```",
        ""
    )

    return code.strip()