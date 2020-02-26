import http.server
import socketserver
from os import curdir, sep

PORT = 8000

class MyHandler(http.server.BaseHTTPRequestHandler):
    '''
    def do_HEAD(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
    '''
    def do_GET(self):
        if self.path == '':
            self.respond({'status': 200})
        else:
            self.respond({'status': 500})

    def handle_http(self, status_code, path):
        f = open(curdir + '/index.html')
        self.send_response(status_code)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        page = f.read()
        f.close()
        return bytes(page, 'UTF-8')

    def respond(self, opts):
        response = self.handle_http(opts['status'], self.path)
        self.wfile.write(response)

with socketserver.TCPServer(("", PORT), MyHandler) as httpd:
    print("serving at port", PORT)
    httpd.serve_forever()
