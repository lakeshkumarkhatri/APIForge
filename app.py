import streamlit as st

from datetime import datetime

from Agents.error_classifier import (
    classify_error
)

from Agents.repair_memory import (
    save_repair_log,
    get_recent_repairs
)

from Core.code_generator import (
    generate_code
)

from Agents.repair_agent import (
    repair_code
)

from Core.validator import (
    validate_inputs
)

from Core.prompt_builder import (
    build_prompt,
    build_scenario_prompt,
    build_universal_scenario_prompt
)

from Core.parser import (
    parse_key_value_input,
    parse_body_input
)

from Core.auth_handler import (
    build_auth_instruction
)

from Core.curl_parser import (
    parse_curl
)

from Core.file_handler import (
    save_code
)

from Core.executor import (
    run_generated_code
)


# ── PAGE CONFIG ───────────────────────────────────────────
st.set_page_config(
    page_title="APIForge",
    layout="wide"
)

# ── SESSION INIT ──────────────────────────────────────────
if "generated_code" not in st.session_state:
    st.session_state["generated_code"] = None

if "filename" not in st.session_state:
    st.session_state["filename"] = None

if "stdout" not in st.session_state:
    st.session_state["stdout"] = None

if "stderr" not in st.session_state:
    st.session_state["stderr"] = None

if "repaired_code" not in st.session_state:
    st.session_state["repaired_code"] = None

if "repair_history" not in st.session_state:
    st.session_state["repair_history"] = []

if "scenario_code" not in st.session_state:
    st.session_state["scenario_code"] = None

if "scenario_language" not in st.session_state:
    st.session_state["scenario_language"] = "cypress"

if "client_instructions" not in st.session_state:
    st.session_state["client_instructions"] = ""


# ── UI HEADER ─────────────────────────────────────────────
st.title("🚀 APIForge")
st.caption("AI-Powered API Code Generation, Execution and Repair")
st.divider()

# ── SIDEBAR ───────────────────────────────────────────────
with st.sidebar:

    st.header("⚙ APIForge Control Panel")

    mode = st.radio(
        "Choose Input Mode",
        [
            "Manual",
            "Smart Paste",
            "Scenario Generator"
        ]
    )

    st.divider()

    # ── CLIENT INSTRUCTIONS ───────────────────────────────
    st.subheader("📋 Generation Instructions")

    st.caption(
        "Optional guidance applied to every generation. "
        "Cleared on browser refresh."
    )

    client_instructions_input = st.text_area(
        "Instructions",
        value=st.session_state["client_instructions"],
        height=150,
        placeholder=(
            "e.g.\n"
            "Keep tests concise\n"
            "One field-specific invalid only\n"
            "Focus on request contract\n"
            "Avoid duplicate validations"
        ),
        key="instructions_input"
    )

    if client_instructions_input != st.session_state["client_instructions"]:
        st.session_state["client_instructions"] = client_instructions_input

    col_a, col_b = st.columns([2, 1])

    with col_b:
        if st.button("🗑 Clear", use_container_width=True):
            st.session_state["client_instructions"] = ""
            st.rerun()

    if st.session_state["client_instructions"].strip():
        st.success("✅ Instructions active")
    else:
        st.info("No instructions set")

    st.divider()

    st.info(
        """
        APIForge

        AI-Powered API Builder

        Generate → Execute → Repair
        """
    )

# ── MAIN LAYOUT ───────────────────────────────────────────
left_col, right_col = st.columns([2, 1])

with left_col:
    st.subheader("API Input")

with right_col:
    st.subheader("Current Mode")
    st.success(mode)


# ── DEFAULTS ──────────────────────────────────────────────
api_url = ""
method = "GET"
auth_type = "public"
auth_value = ""
headers = {}
params = {}
body = None
response_format = "json"
api_notes = ""


# ══════════════════════════════════════════════════════════
# MANUAL MODE
# ══════════════════════════════════════════════════════════
if mode == "Manual":

    st.subheader("Manual Mode")

    with st.expander("🔹 API Basics", expanded=True):

        col1, col2 = st.columns(2)

        with col1:
            api_url = st.text_input("API URL")
            method = st.selectbox(
                "HTTP Method",
                ["GET", "POST", "PUT", "PATCH", "DELETE"]
            )

        with col2:
            auth_type = st.selectbox(
                "Authentication Type",
                ["public", "basic", "bearer", "api key"]
            )
            auth_value = st.text_input("Authentication Value")

    with st.expander("⚙️ Advanced Options", expanded=False):

        headers_input = st.text_area("Headers")
        params_input = st.text_area("Query Parameters")
        body_input = st.text_area("Request Body")
        response_format = st.selectbox(
            "Response Format",
            ["json", "text", "xml", "none"]
        )
        api_notes = st.text_area("API Notes")

    headers = parse_key_value_input(headers_input)
    params = parse_key_value_input(params_input)
    body = parse_body_input(body_input)

    generate_clicked = st.button("🚀 Generate Code", type="primary")
    st.write("")

    if generate_clicked:

        errors = validate_inputs(api_url, method, auth_type, response_format)

        if errors:
            for error in errors:
                st.error(error)

        else:
            auth_instruction = build_auth_instruction(auth_type, auth_value)

            prompt = build_prompt(
                api_url, method, auth_type, auth_instruction,
                headers, params, body, response_format, api_notes,
                client_instructions=st.session_state["client_instructions"]
            )

            with st.spinner("Generating..."):
                code = generate_code(prompt)

            filename = save_code(code)

            st.session_state["generated_code"] = code
            st.session_state["filename"] = filename
            st.session_state["stdout"] = None
            st.session_state["stderr"] = None
            st.session_state["repaired_code"] = None


# ══════════════════════════════════════════════════════════
# SMART PASTE MODE
# ══════════════════════════════════════════════════════════
elif mode == "Smart Paste":

    st.subheader("Smart Paste Mode")

    curl_text = st.text_area(
        "Paste Curl Command",
        height=220,
        placeholder="Paste curl command here..."
    )

    parsed = parse_curl(curl_text) if curl_text else None

    if parsed:
        st.success("Curl parsed successfully")

        with st.expander("🔍 Parsed Preview", expanded=False):
            st.json(parsed)

        api_url = parsed["url"]
        method = parsed["method"]
        headers = parsed["headers"]
        params = parsed["params"]
        body = parsed["body"]
        auth_type = parsed["auth_type"]
        auth_value = parsed["auth_value"]
        response_format = "json"
        api_notes = ""

    generate_clicked = st.button("🚀 Generate Code", type="primary")
    st.write("")

    if generate_clicked:

        errors = validate_inputs(api_url, method, auth_type, response_format)

        if errors:
            for error in errors:
                st.error(error)

        else:
            auth_instruction = build_auth_instruction(auth_type, auth_value)

            prompt = build_prompt(
                api_url, method, auth_type, auth_instruction,
                headers, params, body, response_format, api_notes,
                client_instructions=st.session_state["client_instructions"]
            )

            with st.spinner("Generating..."):
                code = generate_code(prompt)

            filename = save_code(code)

            st.session_state["generated_code"] = code
            st.session_state["filename"] = filename
            st.session_state["stdout"] = None
            st.session_state["stderr"] = None
            st.session_state["repaired_code"] = None


# ══════════════════════════════════════════════════════════
# SCENARIO GENERATOR MODE
# ══════════════════════════════════════════════════════════
else:

    st.subheader("🧪 Scenario Generator")

    st.caption(
        "Paste anything — API docs, curl, plain English, "
        "mixed language, code snippets. AI will understand and "
        "generate test scenarios automatically."
    )

    st.divider()

    with st.expander("📥 Input", expanded=True):

        scenario_input_mode = st.radio(
            "Input Type",
            [
                "Raw Input (paste anything)",
                "Structured Input (manual fields)"
            ],
            horizontal=True
        )

        st.divider()

        if scenario_input_mode == "Raw Input (paste anything)":

            raw_input = st.text_area(
                "Paste API description, curl, docs, or anything",
                height=250,
                placeholder=(
                    "Examples:\n"
                    "POST /sd/pre-url | auth | body: {file_name, file_type, file_size}\n\n"
                    "or paste a curl command\n\n"
                    "or write in plain English: create a login api with email and password"
                )
            )

        else:

            col1, col2 = st.columns(2)

            with col1:
                s_api_url = st.text_input("API URL", key="s_url")
                s_method = st.selectbox(
                    "HTTP Method",
                    ["GET", "POST", "PUT", "PATCH", "DELETE"],
                    key="s_method"
                )

            with col2:
                s_auth_type = st.selectbox(
                    "Authentication Type",
                    ["public", "basic", "bearer", "api key"],
                    key="s_auth"
                )
                s_auth_value = st.text_input(
                    "Authentication Value",
                    key="s_auth_val"
                )

            s_body_input = st.text_area(
                "Request Body",
                key="s_body",
                placeholder='{"field_name": "string", "field_name2": 0}'
            )

            s_params_input = st.text_area(
                "Query Parameters",
                key="s_params"
            )

            s_api_notes = st.text_area(
                "API Notes",
                key="s_notes"
            )

    with st.expander("⚙️ Output Settings", expanded=True):

        output_language = st.radio(
            "Output Language",
            ["Cypress", "Python"],
            horizontal=True
        )

        st.session_state["scenario_language"] = output_language.lower()

    generate_scenarios_clicked = st.button(
        "🧪 Generate Scenarios",
        type="primary"
    )

    if generate_scenarios_clicked:

        lang = st.session_state["scenario_language"]

        if scenario_input_mode == "Raw Input (paste anything)":

            if not raw_input or not raw_input.strip():
                st.error("Please paste some API input first.")

            else:
                with st.spinner("Analysing input and generating scenarios..."):
                    prompt = build_universal_scenario_prompt(
                        raw_input=raw_input,
                        output_language=lang,
                        client_instructions=st.session_state["client_instructions"]
                    )
                    scenario_code = generate_code(prompt)

                st.session_state["scenario_code"] = scenario_code

        else:

            s_errors = validate_inputs(
                s_api_url,
                s_method,
                s_auth_type,
                "json"
            )

            if s_errors:
                for error in s_errors:
                    st.error(error)

            else:
                s_auth_instruction = build_auth_instruction(
                    s_auth_type,
                    s_auth_value
                )

                s_body = parse_body_input(s_body_input)
                s_params = parse_key_value_input(s_params_input)

                with st.spinner("Generating scenarios..."):
                    prompt = build_scenario_prompt(
                        api_url=s_api_url,
                        method=s_method,
                        auth_type=s_auth_type,
                        auth_instruction=s_auth_instruction,
                        headers={},
                        params=s_params,
                        body=s_body,
                        response_format="json",
                        api_notes=s_api_notes,
                        output_language=lang,
                        client_instructions=st.session_state["client_instructions"]
                    )
                    scenario_code = generate_code(prompt)

                st.session_state["scenario_code"] = scenario_code

    if st.session_state["scenario_code"]:

        st.divider()
        st.subheader("🧪 Generated Scenarios")

        lang = st.session_state["scenario_language"]

        display_language = "javascript" if lang == "cypress" else "python"
        file_extension = "cy.js" if lang == "cypress" else "py"
        file_mime = (
            "text/javascript"
            if lang == "cypress"
            else "text/x-python"
        )

        st.code(
            st.session_state["scenario_code"],
            language=display_language
        )

        st.download_button(
            label=f"⬇ Download Scenarios (.{file_extension})",
            data=st.session_state["scenario_code"],
            file_name=f"api_scenarios.{file_extension}",
            mime=file_mime
        )


# ══════════════════════════════════════════════════════════
# GENERATED CODE SECTION
# ══════════════════════════════════════════════════════════
if mode in ["Manual", "Smart Paste"] and st.session_state["generated_code"]:

    st.divider()
    st.subheader("💻 Generated Code")

    st.code(
        st.session_state["generated_code"],
        language="python"
    )

    st.download_button(
        label="⬇ Download Generated Code",
        data=st.session_state["generated_code"],
        file_name="generated_code.py",
        mime="text/x-python"
    )

    st.divider()
    st.subheader("▶ Execution")

    if st.button("Run Generated Code"):

        with st.spinner("Running..."):
            stdout, stderr = run_generated_code(
                st.session_state["filename"]
            )

        st.session_state["stdout"] = stdout
        st.session_state["stderr"] = stderr

    if st.session_state["stderr"]:

        title, message = classify_error(st.session_state["stderr"])

        st.error(title)
        st.info(message)

        with st.expander("View Technical Error"):
            st.code(st.session_state["stderr"])

    elif st.session_state["stdout"]:

        st.success(st.session_state["stdout"])

    else:
        st.info("Click 'Run Generated Code' to execute.")

    if st.session_state["stderr"]:

        st.divider()
        st.subheader("🛠 Repair")

        if st.button("Attempt Repair"):

            with st.spinner("Repairing..."):
                repaired_code = repair_code(
                    st.session_state["generated_code"],
                    st.session_state["stderr"]
                )

            st.session_state["repaired_code"] = repaired_code

        if st.session_state["repaired_code"]:

            st.subheader("Repaired Code")

            st.code(
                st.session_state["repaired_code"],
                language="python"
            )

            st.download_button(
                label="⬇ Download Repaired Code",
                data=st.session_state["repaired_code"],
                file_name="repaired_code.py",
                mime="text/x-python"
            )

            repaired_filename = save_code(
                st.session_state["repaired_code"]
            )

            if st.button("Run Repaired Code"):

                with st.spinner("Running repaired code..."):
                    stdout, stderr = run_generated_code(repaired_filename)

                success = not stderr

                st.session_state["repair_history"].append(
                    {
                        "timestamp": datetime.now().isoformat(),
                        "error": st.session_state["stderr"],
                        "repair": st.session_state["repaired_code"],
                        "success": success
                    }
                )

                if stderr:
                    st.error(stderr)
                elif stdout:
                    st.success(stdout)

        st.divider()
        st.subheader("Repair History")

        history = st.session_state["repair_history"]

        if history:
            for item in reversed(history):
                with st.expander(
                    f"{item['timestamp']} | Success: {item['success']}"
                ):
                    st.write("Error:")
                    st.code(item["error"])

                    st.write("Repair Preview:")
                    st.code(item["repair"])

        else:
            st.info("No repair history yet.")