import threading
import unittest
from http.server import HTTPServer
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import HTTPRedirectHandler, Request, build_opener, urlopen

from src.linear_probe_hash_table import LinearProbeHashTable
from src.server import create_handler
from src.shortener import Shortener


class ServerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = HTTPServer(
            ("127.0.0.1", 0),
            create_handler(Shortener(), Shortener(LinearProbeHashTable)),
        )
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base_url = f"http://127.0.0.1:{cls.server.server_port}"

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()

    def test_form_and_table_page(self):
        with urlopen(self.base_url + "/") as response:
            self.assertEqual(response.status, 200)
            self.assertIn(b"action='/shorten'", response.read())
        with urlopen(self.base_url + "/table") as response:
            self.assertIn(b"Horner recurrence", response.read())

    def test_post_creates_link_and_link_redirects(self):
        request = Request(
            self.base_url + "/shorten",
            data=urlencode({"url": "https://example.com/a"}).encode(),
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        with urlopen(request) as response:
            body = response.read().decode()
            self.assertEqual(response.status, 200)
        self.assertIn("Short URL created", body)
        class NoRedirect(HTTPRedirectHandler):
            def redirect_request(self, request, response, code, message, headers, new_url):
                return None

        with self.assertRaises(HTTPError) as redirect:
            build_opener(NoRedirect).open(self.base_url + "/0")
        self.assertEqual(redirect.exception.code, 302)
        self.assertEqual(redirect.exception.headers["Location"], "https://example.com/a")

    def test_invalid_form_and_unknown_code_return_appropriate_errors(self):
        request = Request(
            self.base_url + "/shorten",
            data=urlencode({"url": "not a URL"}).encode(),
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        with self.assertRaises(HTTPError) as error:
            urlopen(request)
        self.assertEqual(error.exception.code, 400)
        with self.assertRaises(HTTPError) as error:
            urlopen(self.base_url + "/not-found")
        self.assertEqual(error.exception.code, 404)

    def test_table_page_compares_two_colliding_urls(self):
        urls = ("https://www.yonsei.ac.kr", "https://www.google.com")
        for url in urls:
            request = Request(
                self.base_url + "/shorten",
                data=urlencode({"url": url}).encode(),
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
            with urlopen(request) as response:
                self.assertEqual(response.status, 200)

        with urlopen(self.base_url + "/table") as response:
            page = response.read().decode()

        for url in urls:
            self.assertIn(url, page)
        self.assertIn("Separate chaining", page)
        self.assertIn("Linear probing", page)
        self.assertIn("Initial hash slot: 2", page)
        self.assertIn("Visited slots: 2 → 3", page)
        self.assertIn("Final storage slot: 3", page)
        self.assertIn("Horner:", page)


if __name__ == "__main__":
    unittest.main()
