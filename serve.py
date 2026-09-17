#!/usr/bin/env python3
"""
India Trade Dashboard — web server
Local:  python serve.py
Render: python serve.py
"""
import http.server
import json
import os
import socketserver
import urllib.parse

PORT = int(os.environ.get("PORT", "8000"))
BASE = os.path.dirname(os.path.abspath(__file__))

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=BASE, **kwargs)

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)

        # API: list xlsx files in a folder
        if parsed.path == "/api/files":
            params = urllib.parse.parse_qs(parsed.query)
            folder = params.get("folder", [""])[0]

            # Only allow the two dashboard data folders
            if folder not in ("hs2", "hs6"):
                self.send_error(400, "folder must be hs2 or hs6")
                return

            dir_path = os.path.join(BASE, folder)
            try:
                files = sorted(
                    f for f in os.listdir(dir_path)
                    if f.lower().endswith(".xlsx")
                )
            except FileNotFoundError:
                files = []

            body = json.dumps(files).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(body)
            return

        # Everything else: static files (index.html, XLSX files, etc.)
        super().do_GET()

    def log_message(self, fmt, *args):
        pass

class ReusableTCPServer(socketserver.TCPServer):
    allow_reuse_address = True

if __name__ == "__main__":
    print("India Trade Dashboard")
    print(f"Serving on 0.0.0.0:{PORT}")
    with ReusableTCPServer(("0.0.0.0", PORT), Handler) as httpd:
        httpd.serve_forever()
