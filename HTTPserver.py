from http.server import BaseHTTPRequestHandler
from http.server import HTTPServer
from socketserver import ThreadingMixIn
import threading
from os import curdir, sep

PORT = 8000

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
	'''Handle requests in a separate thread'''
	pass

class MyHandler(BaseHTTPRequestHandler):
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
try:
	httpd = ThreadedHTTPServer(('localhost', PORT), MyHandler)
	print("serving at port", PORT)
	print('Use <Ctrl-C> to stop')
	httpd.serve_forever()
except Exception:
	pass
