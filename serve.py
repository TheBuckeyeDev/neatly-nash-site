#!/usr/bin/env python3
"""Static file server for dist/ that avoids os.getcwd() (broken in this sandbox)."""
import functools
import http.server

DIST = "/Users/nicholashalliwell/Downloads/design_handoff_neatly_nash_site/site/dist"
Handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=DIST)

if __name__ == "__main__":
    httpd = http.server.ThreadingHTTPServer(("127.0.0.1", 4173), Handler)
    httpd.serve_forever()
