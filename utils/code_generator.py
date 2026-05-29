import secrets
import string


def generate_numeric_code(length=6):
    """
    Generate a cryptographically secure numeric code.

    Args:
        length (int): Length of the code (default: 6)

    Returns:
        str: A numeric string of the given length (e.g. "048371")
    """
    return "".join(secrets.choice(string.digits) for _ in range(length))


def generate_alphanumeric_code(length=6):
    """
    Generate a cryptographically secure alphanumeric code (uppercase + digits).

    Args:
        length (int): Length of the code (default: 6)

    Returns:
        str: An alphanumeric string of the given length (e.g. "A3K9F2")
    """
    alphabet = string.ascii_uppercase + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))
