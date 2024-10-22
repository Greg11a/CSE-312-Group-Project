import re
from urllib.parse import parse_qs


def extract_credential(encoded_string):
    parsed_data = parse_qs(encoded_string)

    username = parsed_data.get("username", [None])[0]
    password = parsed_data.get("password", [None])[0]

    if not username or not password:
        raise ValueError("Username or password is missing.")

    return username, password


def validate_password(password):
    if len(password) <= 8:
        return False, "Password must be longer than 8 characters."

    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter."

    if not re.search(r"[a-z]", password):
        return False, "Password must contain at least one lowercase letter."

    if not re.search(r"[0-9]", password):
        return False, "Password must contain at least one digit."

    if not re.search(r"[!@#$%^&*_+\-=(),]", password):
        return (
            False,
            "Password must contain at least one special character (!@#$%^&*_+-=(),).",
        )

    return True, "Password is valid."
