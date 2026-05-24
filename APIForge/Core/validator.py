def validate_inputs(
    api_url,
    method,
    auth_type,
    response_format
):
    errors = []

    method = method.strip().upper()
    auth_type = auth_type.strip().lower()
    response_format = response_format.strip().lower()

    # URL validation
    if not api_url.startswith("http"):
        errors.append("Invalid API URL.")
    
    # Method validation
    valid_methods = ["GET", "POST", "PUT", "PATCH", "DELETE"]

    if method not in valid_methods:
        errors.append(
            f"Invalid HTTP Method. Use: {', '.join(valid_methods)}"
        )

    # Auth validation
    valid_auth = [
        "public",
        "basic",
        "api key",
        "bearer",
        "custom header"
    ]

    if auth_type.lower() not in valid_auth:
        errors.append(
            f"Invalid Authentication Type. Use: {', '.join(valid_auth)}"
        )

    # Response format validation
    valid_formats = [
        "json",
        "text",
        "xml",
        "file",
        "none"
    ]

    if response_format.lower() not in valid_formats:
        errors.append(
            f"Invalid Response Format. Use: {', '.join(valid_formats)}"
        )

    return errors