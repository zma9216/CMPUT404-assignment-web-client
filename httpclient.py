#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002,
# https://github.com/treedust, and ZiQing Ma
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
# you may use urllib to encode data appropriately
from urllib.parse import urlparse

DEFAULT_PORT = 80
CRLF = "\r\n"
LF = "\n"


def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    def get_host(self, url):
        return urlparse(url).hostname

    def get_host_port(self,url):
        port = urlparse(url).port
        if port == None:
            port = DEFAULT_PORT
        return port

    def get_path(self, url):
        path = urlparse(url).path
        if path == "":
            path += "/"
        return path

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    """
    Ricky Wilson - https://stackoverflow.com/a/23050458
    get_code(), get_headers(), and get_body() were based on
    Ricky's solution, hence it looks a bit convoluted
    """
    def get_code(self, data):
        request_line = data.split(LF)[0]
        code = int(request_line.split()[1])
        return code

    def get_headers(self, data):
        headers = data.split(CRLF, 1)[0]
        request_line = headers.split(LF)[0]
        headers.replace(request_line, "")
        return headers

    def get_body(self, data):
        headers = self.get_headers(data)
        request_line = headers.split(LF)[0]
        body = data.replace(headers, "")
        body.replace(request_line, "")
        return body

    def parse_args(self, params):
        if params:
            # CryptoFool - https://stackoverflow.com/a/64829960
            data = "&".join([k if v is None else f"{k}={v}" for k, v in params.items()])
        else:
            data = ""
        return data
    
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        
    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')

    def transceive(self, host, port, message):
        self.connect(host, port)
        self.sendall(message)
        data = self.recvall(self.socket)
        self.close()
        return data

    def GET(self, url, args=None):
        host = self.get_host(url)
        port = self.get_host_port(url)
        path = self.get_path(url)
        message = "GET %s HTTP/1.1%s" % (path, CRLF)
        message += "Host: %s" % (host + CRLF)
        message += "Connection: close%s" % (CRLF + CRLF)
        data = self.transceive(host, port, message)
        code = self.get_code(data)
        body = self.get_body(data)
        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        host = self.get_host(url)
        port = self.get_host_port(url)
        path = self.get_path(url)
        params = self.parse_args(args)
        message = "POST %s HTTP/1.1%s" % (path, CRLF)
        message += "Host: %s" % (host + CRLF)
        message += "Connection: close%s" % (CRLF)
        message += "Content-Type: application/x-www-form-urlencoded%s" % (CRLF)
        message += "Content-Length: %d%s" % (len(params), CRLF + CRLF)
        message += params
        data = self.transceive(host, port, message)
        code = self.get_code(data)
        body = self.get_body(data)
        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))
