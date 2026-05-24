def save_code(code):
    filename = "generated_code.py"

    with open(filename, "w", encoding="utf-8") as file:
        file.write(code)

    return filename