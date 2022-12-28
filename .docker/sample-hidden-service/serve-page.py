import os
from dotenv import load_dotenv
from http.server import BaseHTTPRequestHandler, HTTPServer


class web_server(BaseHTTPRequestHandler):

    def do_GET(self):
        if self.path == '/':
            self.path = '/usr/share/index.html'
        try:
            #Reading the file
            file_to_open = open(self.path[1:]).read()
            self.send_response(200)
        except:
            file_to_open = "File not found"
            self.send_response(404)
        self.end_headers()
        self.wfile.write(bytes(file_to_open, 'utf-8'))

load_dotenv('/usr/share/.env')
httpd = HTTPServer(('0.0.0.0', int(os.getenv('SAMPLE_HTTP_SERVICE_PORT'))), web_server)
httpd.serve_forever()
