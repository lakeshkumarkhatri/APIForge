def parse_key_value_input(text):
    text = text.strip()

    if text.lower() == "none":
        return {}

    result = {}

    lines = text.split(",")

    for line in lines:
        if ":" in line:
            key, value = line.split(":", 1)
            result[key.strip()] = value.strip()

    return result


def parse_body_input(body_text):
    body_text = body_text.strip()

    if body_text.lower() == "none":
        return {}

    result = {}

    lines = body_text.split(",")

    for line in lines:
        if ":" in line:
            key, value = line.split(":", 1)
            result[key.strip()] = value.strip()

    return result