#!/usr/bin/env python3
"""Dev server for Ael's Mirror: serves the UI and runs explorer commands."""

import http.server
import json
import os
import shlex
import subprocess
import sys
import urllib.parse

PORT = 8420
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DOCS_DIR = os.path.join(BASE_DIR, "docs")
EXPLORER = os.path.join(BASE_DIR, "aels-mirror-explore.py")


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DOCS_DIR, **kwargs)

    def do_POST(self):
        if self.path == "/run":
            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length))
            cmd = body.get("command", "").strip()
            if not cmd:
                self._json_response({"output": "No command provided.", "error": True})
                return
            try:
                args = shlex.split(cmd)
            except ValueError as e:
                self._json_response({"output": f"Parse error: {e}", "error": True})
                return
            try:
                result = subprocess.run(
                    [sys.executable, EXPLORER] + args,
                    capture_output=True, text=True, timeout=10, cwd=BASE_DIR,
                )
                output = result.stdout
                if result.returncode != 0 and result.stderr:
                    output += f"\n[stderr] {result.stderr}"
                self._json_response({"output": output})
            except subprocess.TimeoutExpired:
                self._json_response({"output": "Command timed out.", "error": True})
            except Exception as e:
                self._json_response({"output": f"Error: {e}", "error": True})
        else:
            self.send_error(404)

    def _json_response(self, data):
        body = json.dumps(data).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", len(body))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def log_message(self, format, *args):
        if "/run" in str(args[0]) if args else False:
            super().log_message(format, *args)


if __name__ == "__main__":
    print(f"Ael's Mirror — http://localhost:{PORT}")
    print(f"  Serving UI from {DOCS_DIR}")
    print(f"  Explorer: {EXPLORER}")
    server = http.server.HTTPServer(("", PORT), Handler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
