import re
import json

def parse_curl(curl_text):

    result = {
        "url": "",
        "method": "GET",
        "headers": {},
        "body": {},
        "auth_type": "public",
        "auth_value": "none",
        "params": {}
    }

    # CLEAN multiline curl
    curl_text = (
        curl_text
        .replace("\\\n", " ")
        .replace("\n", " ")
    )

    # URL
    url_match = re.search(
        r'https?://[^\s"\']+',
        curl_text
    )

    if url_match:
        result["url"] = (
            url_match.group()
        )

    # METHOD
    method_match = re.search(
        r'(?:-X|--request)\s+(\w+)',
        curl_text
    )

    if method_match:
        result["method"] = (
            method_match
            .group(1)
            .upper()
        )

    # HEADERS
    header_matches = re.findall(
        r'(?:-H|--header)\s+"([^:]+):\s*([^"]+)"',
        curl_text
    )

    for key, value in header_matches:

        key = key.strip()
        value = value.strip()

        result["headers"][
            key
        ] = value

        # BEARER AUTH
        if (
            key.lower()
            == "authorization"
        ):

            if value.lower().startswith(
                "bearer "
            ):

                result[
                    "auth_type"
                ] = "bearer"

                result[
                    "auth_value"
                ] = value.replace(
                    "Bearer ",
                    ""
                )

    # BASIC AUTH
    basic_match = re.search(
        r'-u\s+([^\s]+)',
        curl_text
    )

    if basic_match:

        result[
            "auth_type"
        ] = "basic"

        result[
            "auth_value"
        ] = basic_match.group(
            1
        )

    # BODY
    data_match = re.search(
        r'(?:-d|--data|--data-raw)\s+[\'"](.+)[\'"]',
        curl_text
    )

    if data_match:

        raw_data = (
            data_match.group(1)
        )

        try:
            result["body"] = (
                json.loads(
                    raw_data
                )
            )

        except:
            result["body"] = raw_data

    # QUERY PARAMS
    if "?" in result["url"]:

        url_parts = (
            result["url"]
            .split("?", 1)
        )

        result["url"] = (
            url_parts[0]
        )

        query = url_parts[1]

        pairs = query.split("&")

        for pair in pairs:

            if "=" in pair:

                k, v = (
                    pair.split(
                        "=",
                        1
                    )
                )

                result[
                    "params"
                ][k] = v

    return result