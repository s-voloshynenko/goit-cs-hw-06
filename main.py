import os
import socket
import json
from http.server import SimpleHTTPRequestHandler, HTTPServer
from datetime import datetime
from multiprocessing import Process
from pymongo import MongoClient
from urllib.parse import parse_qs

# HTTP Server
class CustomHTTPRequestHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.path = '/index.html'
        elif self.path == '/message.html':
            self.path = '/message.html'
        elif self.path.startswith('/static/'):
            pass  # Serve static files
        else:
            self.path = '/error.html'
        return super().do_GET()

    def do_POST(self):
        if self.path == '/message':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)

            if self.headers.get('Content-Type') == 'application/json':
                data = json.loads(post_data.decode('utf-8'))
            else:
                form_data = parse_qs(post_data.decode('utf-8'))
                data = {
                    "username": form_data.get("username", [""])[0],
                    "message": form_data.get("message", [""])[0]
                }

            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                sock.sendto(json.dumps(data).encode('utf-8'), ('localhost', 5000))

            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'Message sent successfully!')

def run_http_server():
    server_address = ('', 3000)
    httpd = HTTPServer(server_address, CustomHTTPRequestHandler)
    print("HTTP Server running on port 3000...")
    httpd.serve_forever()

def run_socket_server():
    client = MongoClient('mongodb://mongo:27017/')
    db = client['messages_db']
    collection = db['messages']

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.bind(('localhost', 5000))
        print("Socket Server running on port 5000...")
        while True:
            data, _ = sock.recvfrom(1024)
            message = json.loads(data.decode('utf-8'))
            message['date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
            collection.insert_one(message)

if __name__ == '__main__':
    Process(target=run_http_server).start()
    Process(target=run_socket_server).start()
