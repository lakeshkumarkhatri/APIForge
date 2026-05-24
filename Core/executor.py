import subprocess

def run_generated_code(filename):
    try:
        result = subprocess.run(
            ["python", filename],
            capture_output=True,
            text=True
        )

        stdout = result.stdout
        stderr = result.stderr

        error_keywords = [
            "error",
            "exception",
            "failed",
            "connection error",
            "http error",
            "timeout"
        ]

        detected_error = any(
            keyword in stdout.lower()
            for keyword in error_keywords
        )

        if detected_error and not stderr:
            stderr = stdout

        return stdout, stderr

    except Exception as e:
        return "", str(e)