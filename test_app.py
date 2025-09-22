#!/usr/bin/env python3
"""
Application de test simple pour Railway
"""

import os
from http.server import HTTPServer, BaseHTTPRequestHandler

class TestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health/':
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'OK')
        elif self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            html = """
            <!DOCTYPE html>
            <html>
            <head><title>EXEO Portal - Test</title></head>
            <body>
            <h1>🚀 EXEO Portal v3 est en ligne !</h1>
            <p>Application de test déployée avec succès sur Railway (version finale)</p>
                <p>Port: {}</p>
                <p>Status: ✅ Fonctionnel</p>
            </body>
            </html>
            """.format(os.environ.get('PORT', 8000))
            self.wfile.write(html.encode())
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'Not Found')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    print(f"Starting test server on port {port}")
    server = HTTPServer(('0.0.0.0', port), TestHandler)
    server.serve_forever()
