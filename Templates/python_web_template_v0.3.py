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
timeout = 5

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

def get_session(url,headers):
    """
    In: URL, HTTP Headers
    Performs: Initial call to receive session ID
    Out: Python requests Session
    """
    session = requests.session()
    r = session.get(url,headers=headers,timeout=timeout,verify=False)
    return session

def do_request(url,headers,session):
    """
    In: URL, HTTP Headers, Python requests session
    Performs: Example cookie handling and HTTP GET call
    Out: Python requests
    """
    cookie_key_value = {key:value}
    cookie_dummy = {'DUMMY':'DUMMYVAL'}
    requests.utils.add_dict_to_cookiejar(session.cookies, cookie_key_value)
    requests.utils.add_dict_to_cookiejar(session.cookies, cookie_dummy)
    r = session.get(url,headers=headers,timeout=timeout,allow_redirects=False,verify=False)
    return r

#######
# ANY OTHER FUNCTION HERE
#######

# Main
def main(argv):
    if len(sys.argv) == 3:
        host = sys.argv[1]
        port = sys.argv[2]
    else:
        print("[*] Usage: " + sys.argv[0] + " <host> <port>\n")
        exit(0)

    # Do stuff
    try:
        session = get_session(url,headers)
        do_request(url,headers,session)
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
        print("[!] " + str(e))
        exit(-1)
    except requests.exceptions.HTTPError as e:
        print("[!] Failed with error code - " + e.code + "\n")
        exit(-1)
    except KeyboardInterrupt:
        keyboard_interrupt()

# If we were called as a program, go execute the main function.
if __name__ == "__main__":
    main(sys.argv[1:])
