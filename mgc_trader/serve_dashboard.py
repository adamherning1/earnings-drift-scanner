#!/usr/bin/env python3
"""Simple dashboard server that actually works"""

from http.server import HTTPServer, SimpleHTTPRequestHandler
import os

class DashboardHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.path = '/dashboard_simple.html'
        return SimpleHTTPRequestHandler.do_GET(self)
    
    def end_headers(self):
        # Allow the dashboard to be embedded
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('X-Frame-Options', 'ALLOWALL')
        SimpleHTTPRequestHandler.end_headers(self)

def run_server(port=5001):
    os.chdir('C:\\Users\\adamh\\.openclaw\\workspace\\mgc_trader')
    server_address = ('', port)
    httpd = HTTPServer(server_address, DashboardHandler)
    print(f"\n{'='*50}")
    print(f"   SIMPLE DASHBOARD SERVER")
    print(f"{'='*50}")
    print(f"Dashboard available at:")
    print(f"  http://localhost:{port}")
    print(f"  http://192.168.0.57:{port}")
    print(f"\nThe dashboard shows:")
    print(f"- Position: 2 LONG contracts")
    print(f"- Entry: $4,686.50")
    print(f"- Entry Time: 9:28 AM PT")
    print(f"{'='*50}\n")
    httpd.serve_forever()

if __name__ == '__main__':
    run_server()