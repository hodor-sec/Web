#!/usr/bin/python3
import os
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from http.cookies import SimpleCookie

# Server token
server_token = "Apache"

# Handle CTRL-C
def keyboard_interrupt():
    """Handles keyboardinterrupt exceptions"""
    print("\n\n[*] User requested an interrupt, exiting...")
    exit(0)

def printCookie(cookie):
    for key,morsel in cookie.items():
        print("[*] Cookies:\n" + morsel.key + "=" + morsel.value)
        # Some logic to perform actions when received a specific sessioncookie
        session_cookie = 'session_cookie_name'
        if morsel.key == session_cookie:
            print("[*] Found sessioncookie: " + morsel.key + ". Attempting actions...")
    print("\n")

class serveHTTP(BaseHTTPRequestHandler):
    def do_GET(s):
        all_cookies = SimpleCookie(s.headers.get('Cookie'))
        s.server_version = server_token
        s.sys_version = ''
        s.send_response(200)
        s.send_header("Content-type", "text/html")
        s.end_headers()
        print("\n[*] GET:")
        print("\nPath: " + str(s.path))
        print("\nHeaders:\n" + str(s.headers))
        printCookie(all_cookies)

    def do_POST(s):
        all_cookies = SimpleCookie(s.headers.get('Cookie'))
        s.server_version = server_token
        s.sys_version = ''
        s.send_response(200)
        s.end_headers()
        length = int(s.headers['Content-Length'])
        postVar = s.rfile.read(length)
        print("\n[*] POST:")
        print("\nPath: " + str(s.path))
        print("\nHeaders:\n" + str(s.headers))
        print("Params:\n" +  postVar.decode() + "\n")
        printCookie(all_cookies)

# Main
def main(argv):
    if len(sys.argv) == 2:
        port = int(sys.argv[1])
    else:
        print("[*] Usage: " + sys.argv[0] + " <port>\n")
        exit(0)

    server_class = HTTPServer
    httpd = server_class(('', port), serveHTTP)

    # Do stuff
    try:
        print("[*] Accepting HTTP connections on port " + str(port) + "...")
        httpd.serve_forever()
    except KeyboardInterrupt:
        keyboard_interrupt()

# If we were called as a program, go execute the main function.
if __name__ == "__main__":
    main(sys.argv[1:])
