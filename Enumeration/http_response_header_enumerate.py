#!/usr/bin/python3
import requests
import sys
import os
import re
from random_useragent.random_useragent import Randomize     # Randomize useragent

# Disable SSL/TLS cert warnings
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Set timeout
timeout = 3

# Optionally, use a proxy
# proxy = "http://<user>:<pass>@<proxy>:<port>"
proxy = ""
os.environ['http_proxy'] = proxy
os.environ['HTTP_PROXY'] = proxy
os.environ['https_proxy'] = proxy
os.environ['HTTPS_PROXY'] = proxy

def keyboard_interrupt():
    """Handles keyboardinterrupt exceptions"""
    print("\n\n[*] User requested an interrupt, exiting...")
    exit(1)

# Do the magic
def main(argv):
    if len(sys.argv) == 3:
        fileread = sys.argv[1]
        method = sys.argv[2]
    else:
        print("[*] Usage: " + sys.argv[0] + " <file> <http/https>\n")
        exit(1)

    # URI methods
    methods = ['http','https']

    # Check on used method for URI, http or https
    if method not in methods:
        print("[!] Missing schema to use for URL's, use http or https")
        print("[*] Usage: " + sys.argv[0] + " <file> <http/https>\n")
        exit(1)

    # Randomize useragent
    useragent = Randomize().random_agent('desktop', 'windows')

    # HTTP Headers. Might need modification for each webapplication
    headers = {
        'User-Agent': useragent,
    }

    # Check to see if it is a file to read as an argument
    if os.path.isfile(fileread):
        # File exists and keep going
        with open(fileread) as f:
            lines = f.read().splitlines()
    else:
        # Print error and bail, file not there
        print("[!] The following file does not exist: " + fileread + "\n")
        exit(1)

    # Iterate through file
    for line in lines:
        # Remove URI prefix, prepend it with own chosen method
        line = re.sub('^.*//','',line)
        line = method + "://" + line
        try:
            print(line)
            resp = requests.get(line, verify=False,headers=headers, timeout=timeout, allow_redirects=True)
            for res in resp.history:
                print(res.status_code)
                print('\n'.join('{}: {}'.format(k, v) for k, v in res.headers.items()) + '\n')
            print(resp.status_code)
            print('\n'.join('{}: {}'.format(k, v) for k, v in resp.headers.items()) + '\n')
        except requests.exceptions.Timeout:
            print("[!] Timeout error\n")
        except requests.exceptions.TooManyRedirects:
            print("[!] Too many redirects\n")
        except requests.exceptions.ConnectionError:
            print("[!] Not able to connect to URL\n")
        except requests.exceptions.RequestException as e:
            print("[!] " + e)
        except requests.exceptions.HTTPError as e:
            print("[!] Failed with error code - " + e.code + "\n")
        except KeyboardInterrupt:
            keyboard_interrupt()

# If we were called as a program, go execute the main function.
if __name__ == "__main__":
    main(sys.argv[1:])
