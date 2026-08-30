#!/usr/bin/env python3
from http.server import HTTPServer, BaseHTTPRequestHandler
import os

OUT = "/tmp/hives"
os.makedirs(OUT, exist_ok=True)


class H(BaseHTTPRequestHandler):
    def do_PUT(self):
        name = os.path.basename(self.path.strip("/") or "upload.bin")
        length = int(self.headers.get("Content-Length", "0"))
        data = self.rfile.read(length)
        path = os.path.join(OUT, name)
        with open(path, "wb") as f:
            f.write(data)
        print(f"saved {path} {len(data)}", flush=True)
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"ok")

    def log_message(self, fmt, *args):
        print(fmt % args, flush=True)


HTTPServer(("0.0.0.0", 9001), H).serve_forever()
