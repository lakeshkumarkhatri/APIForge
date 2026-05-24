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
    build_prompt
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


# PAGE CONFIG
st.set_page_config(
    page_title="APIForge",
    layout="wide"
)

# SESSION INIT
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

if "active_tab" not in st.session_state:
    st.session_state["active_tab"] = 0


# UI HEADER
st.title(
    "🚀 APIForge"
)

st.caption(
    "AI-Powered API Code Generation, Execution and Repair"
)

st.divider()

# SIDEBAR
with st.sidebar:

    st.header(
        "⚙ APIForge Control Panel"
    )

    mode = st.radio(
        "Choose Input Mode",
        [
            "Manual",
            "Smart Paste"
        ]
    )

    st.divider()

    st.info(
        """
        APIForge

        AI-Powered API Builder

        Generate → Execute → Repair
        """
    )

# MAIN LAYOUT
left_col, right_col = st.columns(
    [2, 1]
)

with left_col:

    st.subheader(
        "API Input"
    )

with right_col:

    st.subheader(
        "Current Mode"
    )

    st.success(
        mode
    )


# DEFAULTS
api_url = ""
method = "GET"
auth_type = "public"
auth_value = ""
headers = {}
params = {}
body = None
response_format = "json"
api_notes = ""


# MANUAL MODE
if mode == "Manual":

    st.subheader(
        "Manual Mode"
    )

    # BASICS
    with st.expander(
        "🔹 API Basics",
        expanded=True
    ):

        col1, col2 = st.columns(2)

        with col1:

            api_url = st.text_input(
                "API URL"
            )

            method = st.selectbox(
                "HTTP Method",
                [
                    "GET",
                    "POST",
                    "PUT",
                    "PATCH",
                    "DELETE"
                ]
            )

        with col2:

            auth_type = st.selectbox(
                "Authentication Type",
                [
                    "public",
                    "basic",
                    "bearer",
                    "api key"
                ]
            )

            auth_value = st.text_input(
                "Authentication Value"
            )

    # ADVANCED
    with st.expander(
        "⚙️ Advanced Options",
        expanded=False
    ):

        headers_input = st.text_area(
            "Headers"
        )

        params_input = st.text_area(
            "Query Parameters"
        )

        body_input = st.text_area(
            "Request Body"
        )

        response_format = st.selectbox(
            "Response Format",
            [
                "json",
                "text",
                "xml",
                "none"
            ]
        )

        api_notes = st.text_area(
            "API Notes"
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
# SMART PASTE
else:

    st.subheader(
        "Smart Paste Mode"
    )

    curl_text = st.text_area(
        "Paste Curl Command",
        height=220,
        placeholder="Paste curl command here..."
    )

    parsed = (
        parse_curl(curl_text)
        if curl_text
        else None
    )

    if parsed:

        st.success(
            "Curl parsed successfully"
        )

        with st.expander(
            "🔍 Parsed Preview",
            expanded=False
        ):

            st.json(
                parsed
            )

        api_url = parsed[
            "url"
        ]

        method = parsed[
            "method"
        ]

        headers = parsed[
            "headers"
        ]

        params = parsed[
            "params"
        ]

        body = parsed[
            "body"
        ]

        auth_type = parsed[
            "auth_type"
        ]

        auth_value = parsed[
            "auth_value"
        ]

        response_format = "json"
        api_notes = ""


# GENERATE
generate_clicked = st.button(
    "🚀 Generate Code",
    type="primary"
)

st.write("")

if generate_clicked:

    errors = validate_inputs(
        api_url,
        method,
        auth_type,
        response_format
    )

    if errors:

        for error in errors:
            if st.session_state["stderr"]:

                st.error(
                    "Execution failed"
                )

                with st.expander(
                    "View Technical Error"
                ):
                    st.code(
                        st.session_state[
                            "stderr"
                        ]
                    )

    else:

        auth_instruction = (
            build_auth_instruction(
                auth_type,
                auth_value
            )
        )

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

        with st.spinner(
            "Generating..."
        ):

            code = generate_code(
                prompt
            )

        filename = save_code(
            code
        )

        st.session_state[
            "generated_code"
        ] = code

        st.session_state[
            "filename"
        ] = filename

        st.session_state[
            "stdout"
        ] = None

        st.session_state[
            "stderr"
        ] = None

        st.session_state[
            "repaired_code"
        ] = None


# SHOW GENERATED
if st.session_state[
    "generated_code"
]:

    tab1, tab2, tab3 = st.tabs(
        [
            "💻 Generated Code",
            "▶ Execution",
            "🛠 Repair"
        ]
    )

    if st.session_state["active_tab"] == 1:
        st.markdown(
            """
            <script>
            window.parent.document.querySelectorAll('[role="tab"]')[1].click();
            </script>
            """,
            unsafe_allow_html=True
    )

    elif st.session_state["active_tab"] == 2:
        st.markdown(
            """
            <script>
            window.parent.document.querySelectorAll('[role="tab"]')[2].click();
            </script>
            """,
            unsafe_allow_html=True
    )
    # TAB 1
    with tab1:
        st.divider()
        
        st.subheader(
            "Generated Code"
        )

        st.code(
            st.session_state[
                "generated_code"
            ],
            language="python"
        )

        st.download_button(
            label="⬇ Download Generated Code",
            data=st.session_state[
                "generated_code"
            ],
            file_name="generated_code.py",
            mime="text/x-python"
        )

    # TAB 2
    with tab2:

            if st.button(
                 "Run Generated Code"
             ):

                st.session_state[
                    "active_tab"
                ] = 1

            with st.spinner(
                "Running..."
            ):

                stdout, stderr = (
                    run_generated_code(
                        st.session_state[
                            "filename"
                        ]
                    )
                )

            st.session_state[
                "stdout"
            ] = stdout

            st.session_state[
                "stderr"
            ] = stderr

        # SHOW EXECUTION RESULT
        if st.session_state[
            "stderr"
        ]:

            title, message = (
                classify_error(
                    st.session_state[
                        "stderr"
                    ]
                )
            )

            st.error(
                title
            )

            st.info(
                message
            )

            with st.expander(
                "View Technical Error"
            ):

                st.code(
                    st.session_state[
                        "stderr"
                    ]
                )

        elif st.session_state[
            "stdout"
        ]:

            st.success(
                st.session_state[
                    "stdout"
                ]
            )

    # TAB 3
    with tab3:

        if st.session_state[
            "stderr"
        ]:

            if st.button(
                "Attempt Repair"
            ):

                with st.spinner(
                    "Repairing..."
                ):

                    repaired_code = (
                        repair_code(
                            st.session_state[
                                "generated_code"
                            ],
                            st.session_state[
                                "stderr"
                            ]
                        )
                    )

                st.session_state[
                    "repaired_code"
                ] = repaired_code

        if st.session_state[
            "repaired_code"
        ]:

            st.subheader(
                "Repaired Code"
            )

            st.code(
                st.session_state[
                    "repaired_code"
                ],
                language="python"
            )

            st.download_button(
                label="⬇ Download Repaired Code",
                data=st.session_state[
                    "repaired_code"
                ],
                file_name="repaired_code.py",
                mime="text/x-python"
            )

            repaired_filename = save_code(
                st.session_state[
                    "repaired_code"
                ]
            )

            if st.button(
                "Run Repaired Code"
            ):

                with st.spinner(
                    "Running repaired code..."
                ):

                    stdout, stderr = (
                        run_generated_code(
                            repaired_filename
                        )
                    )

                success = not stderr

                st.session_state[
                    "repair_history"
                ].append(
                    {
                        "timestamp":
                        datetime.now().isoformat(),

                        "error":
                        st.session_state[
                            "stderr"
                        ],

                        "repair":
                        st.session_state[
                            "repaired_code"
                        ],

                        "success":
                        success
                    }
                )

                if stderr:

                    st.error(
                        stderr
                    )

                elif stdout:

                    st.success(
                        stdout
                    )

                    # REPAIR HISTORY

        # REPAIR HISTORY

            st.divider()

            st.subheader(
                "Repair History"
            )

            history = st.session_state[
                 "repair_history"
            ]

            if history:

                for item in reversed(
                    history
                ):

                    with st.expander(

                        f"{item['timestamp']} | Success: {item['success']}"

                    ):

                        st.write(
                            "Error:"
                        )

                        st.code(
                            item[
                                "error"
                            ]
                        )

                        st.write(
                            "Repair Preview:"
                        )

                        st.code(
                            item[
                                "repair"
                            ]
                        )

            else:

                st.info(
                    "No repair history yet."
                )