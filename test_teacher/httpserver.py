# coding = utf-8
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import urllib

from uiautoRun import *
fun = uiautoTest()
class RequestHandler(BaseHTTPRequestHandler):

    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

    def _json_encode(self, data):
        array = data.split('&')
        json_data = {}
        for item in array:
            item = item.split('=', 1)
            json_data[item[0]] = item[1]
        return json_data

    def do_GET(self):
        response = {
            'status':'SUCCESS',
            'data':'hello from server'
        }

        self._set_headers()
        self.wfile.write(bytes(json.dumps(response),encoding='utf-8'))

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        post_data = str(post_data,encoding='utf-8')
        case=json.loads(post_data)
        # retStr = self._post_handler(post_data)
        # print(retStr)
        #执行用例
        test(fun, case)

        response = {
            'status':200,
            'data':'server got your post data'
        }
        self._set_headers()
        self.wfile.write(bytes(json.dumps(response),encoding='utf-8'))

def run():
    port = 9988
    # print('Listening on localhost:%s' % port)
    server = HTTPServer(('', port), RequestHandler)
    server.serve_forever()

run()