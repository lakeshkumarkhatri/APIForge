import json
import os
from datetime import datetime

MEMORY_FILE = "repair_history.json"


def load_repair_history():

    if not os.path.exists(
        MEMORY_FILE
    ):
        return []

    try:

        with open(
            MEMORY_FILE,
            "r",
            encoding="utf-8"
        ) as f:

            return json.load(
                f
            )

    except:

        return []


def save_repair_log(
    error,
    repaired_code,
    success
):

    history = (
        load_repair_history()
    )

    entry = {

        "timestamp":
        datetime.now().isoformat(),

        "error":
        str(error),

        "repair":
        repaired_code[:500],

        "success":
        success
    }

    history.append(
        entry
    )

    with open(
        MEMORY_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            history,
            f,
            indent=2
        )


def get_recent_repairs(
    limit=5
):

    history = (
        load_repair_history()
    )

    return history[
        -limit:
    ]