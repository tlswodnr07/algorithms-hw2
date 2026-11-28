#!/usr/bin/env python3
"""HTTP interface for the in-memory URL shortener."""

import argparse
import html
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlsplit

if __package__:
    from .hash_table import HashTable
    from .linear_probe_hash_table import LinearProbeHashTable
    from .shortener import Shortener
else:
    from hash_table import HashTable
    from linear_probe_hash_table import LinearProbeHashTable
    from shortener import Shortener


def _page(content: str, title: str = "URL Shortener") -> str:
    return (
        "<!doctype html><html lang='ko'><meta charset='utf-8'>"
        f"<title>{html.escape(title)}</title><body><h1>{html.escape(title)}</h1>"
        f"{content}</body></html>"
    )


def _form() -> str:
    return (
        "<form method='post' action='/shorten'>"
        "<label>URL <input type='url' name='url' required></label>"
        "<button type='submit'>Shorten</button></form>"
        "<p><a href='/table'>Inspect hash table</a></p>"
    )


def _render_table(
    table: HashTable[str] | LinearProbeHashTable[str], title: str
) -> str:
    rows = []
    for index in range(table.capacity):
        entries = []
        for key, code in table.bucket_entries(index):
            trace = table.hash_trace(key)
            steps = " → ".join(
                f"({value_before}×31+ord({character!r})) mod {table.capacity}={value_after}"
                for (character, value_after), value_before in zip(
                    trace, [0] + [value for _, value in trace[:-1]]
                )
            ) or "empty key → 0"
            probes = table.probe_trace(key)
            visited_slots = " → ".join(str(position) for position in probes) or "none"
            final_slot = probes[-1] if probes else index
            entries.append(
                f"<li><code>{html.escape(key)}</code> → "
                f"<code>{html.escape(code)}</code><br>"
                f"Initial hash slot: {table._hash(key)}; "
                f"Visited slots: {html.escape(visited_slots)}; "
                f"Final storage slot: {final_slot}<br>"
                f"Horner: {html.escape(steps)}</li>"
            )
        if not entries:
            entries.append("<li><em>empty</em></li>")
        rows.append(
            f"<tr><th>{index}</th><td><ul>{''.join(entries)}</ul></td></tr>"
        )
    return (
        f"<h2>{html.escape(title)}</h2>"
        "<p>Horner recurrence: h = (31 × h + ord(character)) mod capacity.</p>"
        "<table><thead><tr><th>Slot</th><th>Stored URLs and hash/probe details</th>"
        f"</tr></thead><tbody>{''.join(rows)}</tbody></table><p><a href='/'>Home</a></p>"
    )


def _table_page(shortener: Shortener, linear_shortener: Shortener) -> str:
    return (
        "<p>Both tables contain the same submitted URLs. Linear probing scans the "
        "next slot and wraps at the final slot.</p>"
        f"{_render_table(shortener._url_to_code, 'Separate chaining')}"
        f"{_render_table(linear_shortener._url_to_code, 'Linear probing')}"
    )


def create_handler(shortener: Shortener, linear_shortener: Shortener):
    class ShortenerHandler(BaseHTTPRequestHandler):
        def _send(self, status: int, body: str, content_type: str = "text/html; charset=utf-8"):
            encoded = body.encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(encoded)))
            self.end_headers()
            self.wfile.write(encoded)

        def do_GET(self):
            path = urlsplit(self.path).path
            if path == "/":
                self._send(200, _page(_form()))
                return
            if path == "/table":
                self._send(
                    200,
                    _page(_table_page(shortener, linear_shortener), "Hash tables"),
                )
                return

            code = path.removeprefix("/")
            if not code or "/" in code:
                self._send(404, _page("<p>Short code not found.</p>", "Not found"))
                return
            try:
                url = shortener.expand(code)
            except KeyError:
                self._send(404, _page("<p>Short code not found.</p>", "Not found"))
                return
            self.send_response(302)
            self.send_header("Location", url)
            self.send_header("Content-Length", "0")
            self.end_headers()

        def do_POST(self):
            if urlsplit(self.path).path != "/shorten":
                self._send(404, _page("<p>Page not found.</p>", "Not found"))
                return
            try:
                content_length = int(self.headers.get("Content-Length", "0"))
            except ValueError:
                self._send(400, _page("<p>Invalid request body.</p>", "Bad request"))
                return
            if content_length <= 0 or content_length > 16_384:
                self._send(400, _page("<p>Invalid request body size.</p>", "Bad request"))
                return
            content_type = self.headers.get("Content-Type", "").split(";", 1)[0].strip()
            if content_type != "application/x-www-form-urlencoded":
                self._send(415, _page("<p>Expected a URL-encoded form.</p>", "Unsupported media type"))
                return
            body = self.rfile.read(content_length).decode("utf-8", errors="replace")
            form = parse_qs(body, keep_blank_values=True)
            submitted_url = form.get("url", [""])[0]
            try:
                code = shortener.shorten(submitted_url)
                linear_shortener.shorten(submitted_url)
            except ValueError as error:
                message = html.escape(str(error))
                self._send(400, _page(f"<p>{message}</p>{_form()}", "Invalid URL"))
                return
            link = html.escape(f"/{code}", quote=True)
            safe_url = html.escape(submitted_url)
            content = (
                f"<p>Short URL: <a href='{link}'>{link}</a></p>"
                f"<p>Original URL: <code>{safe_url}</code></p>{_form()}"
            )
            self._send(200, _page(content, "Short URL created"))

    return ShortenerHandler


def main():
    parser = argparse.ArgumentParser(description="Run the URL shortener HTTP server")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    if not 1 <= args.port <= 65535:
        parser.error("--port must be between 1 and 65535")
    server = HTTPServer(
        ("", args.port),
        create_handler(Shortener(), Shortener(LinearProbeHashTable)),
    )
    print(f"Serving on port {args.port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping server")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
