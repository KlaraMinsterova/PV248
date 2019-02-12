import sys
import http.client
import http.server
import socket
import json


class Handler(http.server.BaseHTTPRequestHandler):

    def do_GET(self):
        upstream = sys.argv[2].replace('http://', '').replace('https://', '') + '/' + self.path
        upstream = upstream.split('/', 1)
        dict = {}
        code = None
        content = None
        headers = None
        socket.setdefaulttimeout(1)

        try:
            conn = http.client.HTTPConnection(upstream[0], timeout=1)
            if len(upstream) == 2:
                conn.request('GET', '/' + upstream[-1])
            else:
                conn.request('GET', '/')

            response = conn.getresponse()
            headers = response.getheaders()
            code = response.status
            content = response.read().decode('utf-8', 'ignore')
            conn.close()
        except:
            conn.close()

        if code is not None:
            dict['code'] = int(code)
            header_dict = {}
            for header in headers:
                header_dict[header[0]] = header[-1]
            dict['headers'] = header_dict
            try:
                valid_json = json.loads(content.replace('\n', '').replace('\\', ''))
                dict['json'] = valid_json
            except json.decoder.JSONDecodeError:
                dict['content'] = content
        else:
            dict['code'] = 'timeout'

        json_bytes = bytes(str(json.dumps(dict)), 'utf-8')

        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json_bytes)

    def do_POST(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

        dict = {}
        data = self.rfile.read(int(self.headers['Content-Length']))

        try:
            valid_json = json.loads(data)

            if 'url' not in valid_json or (valid_json['type'] == 'POST' and 'content' not in valid_json):
                raise ValueError()

            type = 'GET' if 'type' not in valid_json else valid_json['type']
            timeout = 1 if 'timeout' not in valid_json else valid_json['timeout']
            headers = {} if 'headers' not in valid_json else valid_json['headers']
            url = valid_json['url'].replace('http://', '').replace('https://', '').split('/', 1)
            code = None
            content = None
            socket.setdefaulttimeout(timeout)

            try:
                conn = http.client.HTTPConnection(url[0], timeout=timeout)
                if len(url) == 2:
                    conn.request(type, '/' + url[-1], headers=headers)
                else:
                    conn.request(type, '/', headers=headers)
                response = conn.getresponse()
                headers = response.getheaders()
                code = response.status
                content = response.read().decode('utf-8', 'ignore')
                conn.close()
            except:
                conn.close()

            if code is not None:
                dict['code'] = int(code)
                header_dict = {}
                for header in headers:
                    header_dict[header[0]] = header[-1]
                dict['headers'] = header_dict
                try:
                    valid_json = json.loads(content.replace('\n', '').replace('\\', ''))
                    dict['json'] = valid_json
                except json.decoder.JSONDecodeError:
                    dict['content'] = content
            else:
                dict['code'] = 'timeout'
        except:
            dict['code'] = 'invalid json'

        json_bytes = bytes(str(json.dumps(dict)), 'utf-8')

        self.send_response(200)
        self.end_headers()
        self.wfile.write(json_bytes)


port = int(sys.argv[1])

server = http.server.HTTPServer(('localhost', port), Handler)
server.serve_forever()
