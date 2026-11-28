import unittest

from src.hash_table import HashTable
from src.linear_probe_hash_table import LinearProbeHashTable
from src.shortener import Shortener


class ShortenerTests(unittest.TestCase):
    def test_shortens_and_expands_urls(self):
        shortener = Shortener()
        code = shortener.shorten("https://example.com/a")
        self.assertEqual(shortener.expand(code), "https://example.com/a")

    def test_repeated_url_returns_same_code(self):
        shortener = Shortener()
        first = shortener.shorten("https://example.com/")
        second = shortener.shorten("https://example.com/")
        self.assertEqual(first, second)

    def test_distinct_urls_receive_distinct_codes(self):
        shortener = Shortener()
        first = shortener.shorten("https://example.com/one")
        second = shortener.shorten("https://example.com/two")
        self.assertNotEqual(first, second)

    def test_rejects_invalid_urls(self):
        shortener = Shortener()
        for url in ("", "example.com", "ftp://example.com", "http:///missing", "http://bad host"):
            with self.subTest(url=url):
                with self.assertRaises(ValueError):
                    shortener.shorten(url)

    def test_unknown_code_raises_key_error(self):
        with self.assertRaises(KeyError):
            Shortener().expand("unknown")

    def test_supports_both_hash_table_implementations(self):
        for table_factory in (HashTable, LinearProbeHashTable):
            with self.subTest(table=table_factory.__name__):
                shortener = Shortener(table_factory)
                code = shortener.shorten("https://example.com/")
                self.assertEqual(code, "0")
                self.assertEqual(shortener.expand(code), "https://example.com/")


if __name__ == "__main__":
    unittest.main()
