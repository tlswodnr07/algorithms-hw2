"""Base62 encoding and decoding utilities."""

ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
_BASE = len(ALPHABET)


def encode(number: int) -> str:
    """Encode a non-negative integer as a base62 string."""
    if not isinstance(number, int) or isinstance(number, bool):
        raise TypeError("number must be an integer")
    if number < 0:
        raise ValueError("number must be non-negative")
    if number == 0:
        return ALPHABET[0]

    encoded = []
    while number:
        number, remainder = divmod(number, _BASE)
        encoded.append(ALPHABET[remainder])
    return "".join(reversed(encoded))


def decode(code: str) -> int:
    """Decode a base62 string into a non-negative integer."""
    if not isinstance(code, str):
        raise TypeError("code must be a string")
    if not code:
        raise ValueError("code must not be empty")

    number = 0
    for character in code:
        try:
            digit = ALPHABET.index(character)
        except ValueError as error:
            raise ValueError(f"invalid base62 character: {character!r}") from error
        number = number * _BASE + digit
    return number
