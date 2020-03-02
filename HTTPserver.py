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
    def do_GET(self):
        print('Managing GET request')
        if self.path == '/' or self.path == '/index.html':
        	print('Enter if')
        	self.handle_http_GET(200, self.path)
        else:
	        pass

    def do_POST(self):
        print('Managing POST request')
        if self.path == '/pay':
	        pass
        else:
	        pass

    def handle_http_GET(self, status_code, path):
        if self.path == '/' or self.path == '/index.html':
	        f = open(curdir + '/index.html')
	        self.send_response(status_code)
	        self.send_header('Content-type', 'text/html')
	        self.end_headers()
	        page = f.read()
	        f.close()
	        self.respond(bytes(page,'UTF-8'))

    def handle_http_POST(self, status_code, path):
	        pass


    def respond(self, response):
        self.wfile.write(response)
try:
	httpd = ThreadedHTTPServer(('localhost', PORT), MyHandler)
	print("serving at port", PORT)
	print('Use <Ctrl-C> to stop')
	httpd.serve_forever()
except Exception:
	pass
