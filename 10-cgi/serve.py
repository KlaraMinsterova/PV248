import sys
import os
import socketserver
import http.server
import urllib.parse


class Server(socketserver.ThreadingMixIn, http.server.HTTPServer):
    pass


class RequestHandler(http.server.CGIHTTPRequestHandler):
    def do_HEAD(self):
        self.common_function()

    def do_GET(self):
        self.common_function()

    def do_POST(self):
        self.common_function()

    def common_function(self):
        subdirectory = os.path.dirname(self.path)
        if subdirectory not in self.cgi_directories:
            self.cgi_directories.append(subdirectory)

        if self.is_cgi() and urllib.parse.urlparse(self.path).path.endswith('.cgi'):
            self.run_cgi()
        else:
            value = http.server.SimpleHTTPRequestHandler.send_head(self)
            if value:
                self.copyfile(value, self.wfile)


port = int(sys.argv[1])
directory = sys.argv[2]
os.chdir(os.path.realpath(directory))
server = Server(('', port), RequestHandler)
server.serve_forever()
