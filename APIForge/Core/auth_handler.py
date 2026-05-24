def build_auth_instruction(
    auth_type,
    auth_value
):
    auth_type = auth_type.strip().lower()

    if auth_type == "public":
        return "No authentication required."

    elif auth_type == "bearer":
        return (
            f"Use Bearer token authentication "
            f"with token: {auth_value}"
        )

    elif auth_type == "api key":
        return (
            f"Use API Key authentication "
            f"with key: {auth_value}"
        )

    elif auth_type == "basic":
        return (
            f"Use Basic Authentication "
            f"with credentials: {auth_value}"
        )

    elif auth_type == "custom header":
        return (
            f"Use custom header authentication: "
            f"{auth_value}"
        )

    return "Unknown authentication type."