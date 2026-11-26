import unittest

from src.base62 import decode, encode


class Base62Tests(unittest.TestCase):
    def test_zero_encodes_as_zero(self):
        self.assertEqual(encode(0), "0")

    def test_round_trips_base62_boundaries(self):
        for number in (1, 9, 10, 35, 36, 61, 62, 3844, 2**64):
            with self.subTest(number=number):
                self.assertEqual(decode(encode(number)), number)

    def test_rejects_negative_or_non_integer_input(self):
        with self.assertRaises(ValueError):
            encode(-1)
        with self.assertRaises(TypeError):
            encode("1")

    def test_rejects_empty_or_invalid_codes(self):
        for code in ("", "a+", " ", "你好"):
            with self.subTest(code=code):
                with self.assertRaises(ValueError):
                    decode(code)

    def test_rejects_non_string_code(self):
        with self.assertRaises(TypeError):
            decode(1)


if __name__ == "__main__":
    unittest.main()
