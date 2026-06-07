#!/usr/bin/env python3
"""Simple HTTP server for CodePulse frontend."""
import http.server
import socketserver
import os
import json
from pathlib import Path

PORT = 3000
FRONTEND_DIR = Path(__file__).parent / 'frontend'

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        # Serve index.html for all routes (SPA)
        if self.path == '/' or not Path(FRONTEND_DIR / self.path.lstrip('/')).exists():
            self.path = '/index.html'
        return super().do_GET()

    def end_headers(self):
        # Disable caching for development
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        super().end_headers()

os.chdir(FRONTEND_DIR)

with socketserver.TCPServer(("", PORT), MyHTTPRequestHandler) as httpd:
    print(f"✅ Frontend server running on http://localhost:{PORT}")
    print(f"📁 Serving from: {FRONTEND_DIR}")
    httpd.serve_forever()
