#!/usr/bin/env python3
"""
Serve this repository over HTTP so a client can be developed against it.

A client reads the profiles with plain HTTP GET, which is the whole point of the
layout, so any static file server will do. The one thing a stock
``python3 -m http.server`` does not do is send CORS headers, and without them a
browser refuses the responses when the page is served from a different port.
This serves the same files and adds the header.

    python3 scripts/serve.py 8000

Then point the client at http://localhost:8000, for example by setting
VITE_DOMAIN_PROFILES_URL in the low-code modeler. Intended for development only,
it binds to localhost and serves whatever is in the repository directory.
"""

from __future__ import annotations

import sys
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


class CorsHandler(SimpleHTTPRequestHandler):
    """Static file handler that allows cross-origin reads."""

    def end_headers(self) -> None:
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def log_message(self, fmt: str, *args) -> None:
        # One compact line per request, so a failing path is easy to spot.
        sys.stderr.write(f"{self.address_string()} {fmt % args}\n")


def main() -> None:
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    handler = partial(CorsHandler, directory=str(REPO_ROOT))
    with ThreadingHTTPServer(("127.0.0.1", port), handler) as server:
        print(f"Serving {REPO_ROOT} on http://localhost:{port}")
        print("Point VITE_DOMAIN_PROFILES_URL at that address and restart the modeler.")
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\nStopped.")


if __name__ == "__main__":
    main()
