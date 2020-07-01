#!/usr/bin/python3
import requests
import urllib3
import os
import sys
import re
import inquirer
from tqdm import tqdm
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
timeout = 10

# Prefix
prefix = "1"

# Default string as clean value for parameter
def_str = "1234"

# Handle CTRL-C
def keyboard_interrupt():
    """Handles keyboardinterrupt exceptions"""
    print("\n\n[*] User requested an interrupt, exiting...")
    exit(0)

# Custom HTTP headers
def http_headers():
    # Randomize useragent
    useragent = Randomize().random_agent('desktop', 'windows')
    # HTTP Headers. Might need modification for each webapplication
    headers = {
        'User-Agent': useragent,
    }
    return headers

def norm_req(url,headers,get_post,params):
    norm_params = dict()
    for param in params:
        norm_params[param] = def_str

    # Do GET or POST with a clean value to compare response later
    if get_post.lower() == "get":
        r = requests.get(url,params=norm_params,headers=headers,timeout=timeout,verify=False)
    elif get_post.lower() == "post":
        r = requests.post(url,data=norm_params,headers=headers,timeout=timeout,verify=False)
    
    # Return length of the normal response
    return len(r.content)

# Perform the SQLi call for injection
def sqli(url,headers,get_post,inj_param,params,prefix,norm_resp,ign_len,inj_str):
    inj_params = dict()
    for param in params:
        inj_params[param] = def_str
        if param == inj_param:
            inj_params[param] = prefix + inj_str

    # Do GET or POST with a injected string
    if get_post.lower() == "get":
        r = requests.get(url,params=inj_params,headers=headers,timeout=timeout,verify=False)
    elif get_post.lower() == "post":
        r = requests.post(url,data=inj_params,headers=headers,timeout=timeout,verify=False)

    # Length of the injected response
    inj_resp = len(r.content)

    # Check if response matches ignored lengths
    for ignored_len in ign_len:
        if inj_resp == int(ignored_len):
            return False

    # Return the response if length of responses don't match
    if norm_resp != inj_resp:
        return inj_resp
    else:
        return False

# Main
def main(argv):
    if len(sys.argv) == 7:
        params = sys.argv[1].split(",")
        get_post = sys.argv[2]
        ign_len = sys.argv[3].split(",")
        prefix = sys.argv[4]
        injlist_read = sys.argv[5]
        url = sys.argv[6]
    else:
        print("[*] Usage: " + sys.argv[0] + " <param1,param2,..> <get_or_post> <len_ignore1,len_ignore2,..> <prefix> <file_injection_strings> <url>")
        print("[*] Example: " + sys.argv[0] + " id get 0 \"1' \" /usr/share/wordlists/seclists/Fuzzing/SQLi/Generic-SQLi.txt http://192.168.252.6/cat.php\n")
        exit(-1)

    # Random headers
    headers = http_headers()

    # Read if file exists
    if not os.path.isfile(injlist_read):
        print("[!] Wordlist for injections does not exist. Exiting...")
        exit(-1)

    # Do stuff
    try:
        param_question = [inquirer.List('params',
                message="Select a parameter to test for injection:",
                choices=params),]
        param_answer = inquirer.prompt(param_question)
        inj_param = param_answer["params"]

        # Perform a normal request with the clean parameter string to compare response later
        norm_resp = norm_req(url,headers,get_post,params)

        # Read lines of file and count them
        inj_lines = open(injlist_read)
        len_inj_lines = len(open(injlist_read).readlines())

        # Loop parameters
        print("[*] Testing parameter \"" + inj_param + "\"")

        # Loop the strings in attempting to detect possible SQLi
        for inj_str in tqdm(inj_lines,total=len_inj_lines):
            inj_str = inj_str.strip('\n')
            inj_len = sqli(url,headers,get_post,inj_param,params,prefix,norm_resp,ign_len,inj_str)
            if inj_len:
                print("\n[*] Param \"" + inj_param + "\" using string \"" + prefix + inj_str + "\"")
                print("[*] Original response: " + str(norm_resp))
                print("[*] Returned response: " + str(inj_len) + "\n")

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
        exit(-1)

# If we were called as a program, go execute the main function.
if __name__ == "__main__":
    main(sys.argv[1:])
