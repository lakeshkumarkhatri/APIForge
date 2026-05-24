from Config.config import client, MODEL_NAME

def generate_code(prompt):
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt
    )

    code = response.text

    code = code.replace("```python", "")
    code = code.replace("```", "")
    code = code.strip()

    return code