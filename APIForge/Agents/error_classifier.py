def classify_error(
    error_text
):

    error = str(
        error_text
    ).lower()

    if (
        "401" in error
        or "unauthorized" in error
    ):
        return (
            "🔐 Unauthorized Error",
            "Authentication failed. Check API key, bearer token, or credentials."
        )

    elif (
        "403" in error
        or "forbidden" in error
    ):
        return (
            "⛔ Forbidden Error",
            "Access denied. Permissions may be insufficient."
        )

    elif (
        "404" in error
        or "not found" in error
    ):
        return (
            "🔎 Not Found Error",
            "Endpoint or resource could not be found."
        )

    elif (
        "connectionerror" in error
        or "failed to resolve"
        in error
        or "dns"
        in error
    ):
        return (
            "🌐 Connection Error",
            "Could not connect to host. Check URL or network."
        )

    elif (
        "timeout" in error
    ):
        return (
            "⏳ Timeout Error",
            "Request timed out."
        )

    elif (
        "json"
        in error
        and (
            "decode"
            in error
            or "expecting value"
            in error
        )
    ):
        return (
            "📄 JSON Parsing Error",
            "Response format does not match expected JSON."
        )

    elif (
        "http error"
        in error
        or "client error"
        in error
        or "server error"
        in error
    ):
        return (
            "⚠ HTTP Error",
            "Server returned an HTTP error."
        )

    return (
        "❌ Execution Failed",
        "Unknown execution error."
    )