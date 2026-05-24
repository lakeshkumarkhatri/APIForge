from validator import validate_inputs
from config import client, MODEL_NAME
from prompt_builder import build_prompt
from file_handler import save_code
from executor import run_generated_code
from parser import (
    parse_key_value_input,
    parse_body_input
)
from auth_handler import build_auth_instruction
from repair_agent import repair_code
from curl_parser import parse_curl
from code_generator import generate_code

print("=== API Agent V1 ===")

print("Choose Input Mode")
print("1 - Manual")
print("2 - Smart Paste")

mode = input("Mode: ")

# SMART PASTE MODE
if mode == "2":

    curl_text = input(
        "Paste your curl command: "
    )

    parsed = parse_curl(
        curl_text
    )

    api_url = parsed["url"]
    method = parsed["method"]
    headers = parsed["headers"]
    body = parsed["body"]

    params = parsed["params"]

    print("\nParsed Curl:\n")
    print(parsed)

    auth_type = parsed["auth_type"]
    auth_value = parsed["auth_value"]
    response_format = "json"
    api_notes = ""

# MANUAL MODE
else:

    api_url = input("API URL: ")
    method = input("HTTP Method: ")

    auth_type = input(
        "Authentication Type: "
    )

    auth_value = input(
        "Authentication Value: "
    )

    headers_input = input(
        "Headers: "
    )

    params_input = input(
        "Query Parameters: "
    )

    body_input = input(
        "Request Body: "
    )

    headers = parse_key_value_input(
        headers_input
    )

    params = parse_key_value_input(
        params_input
    )

    body = parse_body_input(
        body_input
    )

    response_format = input(
        "Response Format: "
    )

    api_notes = input(
        "API Notes / Docs (optional): "
    )

# COMMON PIPELINE

auth_instruction = build_auth_instruction(
    auth_type,
    auth_value
)

errors = validate_inputs(
    api_url,
    method,
    auth_type,
    response_format
)

if errors:

    print("\nInput Errors:\n")

    for error in errors:
        print("-", error)

    exit()

prompt = build_prompt(
    api_url,
    method,
    auth_type,
    auth_instruction,
    headers,
    params,
    body,
    response_format,
    api_notes
)

print("\nGenerating code...\n")

code = generate_code(
    prompt
)

print("\nGenerated Code:\n")
print(code)

filename = save_code(
    code
)

print(
    f"\nCode saved to: {filename}"
)

run_choice = input(
    "\nRun generated code? (y/n): "
).lower()

if run_choice == "y":

    print(
        "\nRunning generated code...\n"
    )

    stdout, stderr = run_generated_code(
        filename
    )

    if stdout:
        print(
            "Execution Output:\n"
        )
        print(stdout)

    if stderr:

        print(
            "Execution Errors:\n"
        )
        print(stderr)

        repair_choice = input(
            "\nAttempt auto-repair? (y/n): "
        ).lower()

        if repair_choice == "y":

            print(
                "\nAttempting repair...\n"
            )

            repaired_code = repair_code(
                code,
                stderr
            )

            print(
                "\nRepaired Code:\n"
            )
            print(repaired_code)

            save_code(
                repaired_code
            )