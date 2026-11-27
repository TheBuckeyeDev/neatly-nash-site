#!/usr/bin/env python3
"""Static file server for dist/ that avoids os.getcwd() (broken in some sandboxes)."""
import functools
import http.server
from pathlib import Path

DIST = str(Path(__file__).resolve().parent / "dist")
Handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=DIST)

if __name__ == "__main__":
    httpd = http.server.ThreadingHTTPServer(("127.0.0.1", 4173), Handler)
    httpd.serve_forever()
