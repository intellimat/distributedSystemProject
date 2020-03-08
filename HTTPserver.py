from http.server import BaseHTTPRequestHandler
from http.server import HTTPServer
from socketserver import ThreadingMixIn
import threading
import json
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
			self.handle_http_POST(200, self.path)
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
		data = self.readResponse().decode("utf-8")
		self.parsedData = json.loads(data)
		print('Parsed data: \n')
		print(self.parsedData)

		self.send_response(status_code)
		self.send_header('Content-type', 'text/html')
		self.end_headers()
		print('\n\nFORMING HTML RESPONSE')
		content = '''
		<html><head><title>Title goes here.</title></head>
		<body><p>This is a test.</p>
		<p>You accessed path: {}</p>
		</body></html>
		'''.format(path)
		ca = self.client_address
		print('Client address: ')
		print(ca)
		self.respond(bytes(content,'UTF-8'))
		print('\n\nSENT RESPONSE')
		''' here we gotta call the gateway server'''


	def respond(self, response):
		self.wfile.write(response)

	def readResponse(self):
		length = int(self.headers.get('content-length'))
		dataReceived = self.rfile.read(length)
		return dataReceived
try:
	httpd = ThreadedHTTPServer(('localhost', PORT), MyHandler)
	print("serving at port", PORT)
	print('Use <Ctrl-C> to stop')
	httpd.serve_forever()
except Exception:
	pass
