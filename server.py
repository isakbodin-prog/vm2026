#!/usr/bin/env python3
"""
Lokal proxy för football-data.org → vm2026.html
Kör: python3 server.py
Öppna sedan: http://localhost:8765
"""

import http.server
import urllib.request
import urllib.error
import json
import os

API_TOKEN = os.environ.get('FOOTBALL_API_TOKEN', '634a7a50cdbd4cba8205ca185ab8c78d')
API_BASE  = 'https://api.football-data.org/v4'
PORT      = 8765
HTML_FILE = 'vm2026.html'   # måste ligga i samma mapp som server.py

class Handler(http.server.BaseHTTPRequestHandler):

    def log_message(self, fmt, *args):
        print(f'  {self.address_string()} – {fmt % args}')

    def send_cors(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_cors()
        self.end_headers()

    def do_GET(self):
        # Serve the HTML file at root
        if self.path in ('/', '/vm2026.html'):
            self._serve_html()
        # Proxy /api/* → football-data.org
        elif self.path.startswith('/api/'):
            self._proxy(self.path[4:])   # strip /api
        else:
            self.send_response(404)
            self.end_headers()

    def _serve_html(self):
        try:
            with open(HTML_FILE, 'rb') as f:
                data = f.read()
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Content-Length', len(data))
            self.end_headers()
            self.wfile.write(data)
        except FileNotFoundError:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'vm2026.html not found in current directory')

    def _proxy(self, path):
        url = f'{API_BASE}{path}'
        req = urllib.request.Request(url, headers={'X-Auth-Token': API_TOKEN})
        try:
            with urllib.request.urlopen(req, timeout=10) as r:
                body = r.read()
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_cors()
            self.end_headers()
            self.wfile.write(body)
        except urllib.error.HTTPError as e:
            body = e.read()
            self.send_response(e.code)
            self.send_header('Content-Type', 'application/json')
            self.send_cors()
            self.end_headers()
            self.wfile.write(body)
        except Exception as e:
            self.send_response(502)
            self.send_cors()
            self.end_headers()
            self.wfile.write(json.dumps({'error': str(e)}).encode())

if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    print(f'VM 2026-server startad → http://localhost:{PORT}')
    print(f'Tryck Ctrl+C för att stoppa.\n')
    http.server.HTTPServer(('localhost', PORT), Handler).serve_forever()
