"""In-memory URL shortener backed by the project's hash table."""

from urllib.parse import urlsplit

from src.base62 import encode
from src.hash_table import HashTable


class Shortener:
    def __init__(self):
        self._url_to_code: HashTable[str] = HashTable()
        self._code_to_url: HashTable[str] = HashTable()
        self._next_id = 0

    def shorten(self, url: str) -> str:
        if not isinstance(url, str):
            raise ValueError("URL must be a string")
        if not url or any(character.isspace() for character in url):
            raise ValueError("URL must not be empty or contain whitespace")
        try:
            parsed = urlsplit(url)
            hostname = parsed.hostname
            parsed.port
        except ValueError as error:
            raise ValueError("invalid URL") from error
        if parsed.scheme not in ("http", "https") or not hostname:
            raise ValueError("URL must be an absolute HTTP or HTTPS URL")

        existing_code = self._url_to_code.get(url)
        if existing_code is not None:
            return existing_code

        code = encode(self._next_id)
        self._next_id += 1
        self._url_to_code[url] = code
        self._code_to_url[code] = url
        return code

    def expand(self, code: str) -> str:
        return self._code_to_url[code]
