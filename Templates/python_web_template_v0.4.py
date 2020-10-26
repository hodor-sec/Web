#!/usr/bin/python3
import requests
import urllib3
import os
import sys
import argparse
from urllib.parse import urlparse
from random_useragent.random_useragent import Randomize     # Randomize useragent

# Disable cert warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Set timeout
timeout = 10

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

# Check if URL is an URL
def isurl(urlstr):
    try:
        urlparse(urlstr)
        return urlstr
    except ArgumentTypeError:
        raise argparse.ArgumentTypeError("Invalid URL")

def get_session(target_url,proxies,headers):
    """
    In: URL, HTTP Headers
    Performs: Initial call to receive session ID
    Out: Python requests Session
    """
    session = requests.session()
    r = session.get(target_url,headers=headers,timeout=timeout,allow_redirects=False,verify=False,proxies=proxies)
    return session

def do_request(target_url,proxies,headers,session):
    """
    In: URL, HTTP Headers, Python requests session
    Performs: Example cookie handling and HTTP GET call
    Out: Python requests
    """
    cookie_key_value = {'key':'value'}
    cookie_dummy = {'DUMMY':'DUMMYVAL'}
    requests.utils.add_dict_to_cookiejar(session.cookies, cookie_key_value)
    requests.utils.add_dict_to_cookiejar(session.cookies, cookie_dummy)
    r = session.get(target_url,headers=headers,timeout=timeout,allow_redirects=False,verify=False,proxies=proxies)
    return r

#######
# ANY OTHER FUNCTION HERE
#######

# Main
def main(argv):
    parser = argparse.ArgumentParser(description='Python Web Template')
    parser.add_argument("--url", "-u", type=isurl, required=True, help="The url of the target.")
    parser.add_argument("--proxy", "-p", type=isurl, required=False, help="Example: http://127.0.0.1:8080")
    args = parser.parse_args()
    
    # Check if target URL is valid
    url_parts = urlparse(args.url)
    target_url = "%s://%s" % (url_parts.scheme, url_parts.netloc)
	
    # Set optional proxy
    proxies = {}
    if(args.proxy != None):
        proxy_parts = urlparse(args.proxy)
        proxies = {
            "http": "http://" + proxy_parts.netloc,
            "https": "https://" + proxy_parts.netloc,
        }            

    # Set HTTP Headers
    headers = http_headers()

    # Do stuff
    try:
        session = get_session(target_url,proxies,headers)
        r = do_request(target_url,proxies,headers,session)
        print(r.text)
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
