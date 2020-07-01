#!/usr/bin/python3
import requests
import urllib3
import os
import sys
import re
import inquirer
from tqdm import tqdm
from random_useragent.random_useragent import Randomize     # Randomize useragent
from bs4 import BeautifulSoup

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

# Prefix
prefix = "1"

# Default string for parameters
def_str = "1234"

# Handle CTRL-C
def keyboard_interrupt():
    """Handles keyboardinterrupt exceptions"""
    print("\n\n[*] User requested an interrupt, exiting...")
    exit(1)

# Custom HTTP headers
def http_headers():
    # Randomize useragent
    useragent = Randomize().random_agent('desktop', 'windows')
    # HTTP Headers. Might need modification for each webapplication
    headers = {
        'User-Agent': useragent,
    }
    return headers

# Detect error based on returned response
# Based on XML error list of sqlmap
def detect_error(resp):
    error_list = [
	"42000-192",
	"Access Database Engine",
	"Altibase.jdbc.driver",
	"check the manual that",
	"CLI Driver.DB2",
	"com.facebook.presto.jdbc",
	"com.frontbase.jdbc",
	"com.ibm.db2.jcc",
	"com.informix.jdbc",
	"com.ingres.gcf.jdbc",
	"com.jnetdirect.jsql",
	"com.mckoi.database.jdbc",
	"com.mckoi.JDBCDriver",
	"com.microsoft.sqlserver.jdbc",
	"com.mimer.jdbc",
	"com.mysql.jdbc",
	"comparison operator is required here",
	"com.sap.dbtech.jdbc",
	"com.simba.presto.jdbc",
	"com.sybase.jdbc",
	"com.vertica.dsi.dataengine",
	"com.vertica.jdbc",
	"Data.SQLite.SQLiteException",
	"DB2Exception",
	"DB2 SQL error",
	"DriverSapDB",
	"Drizzle",
	"Dynamic SQL Error",
	"encountered after end of query",
	"error",
	"ERROR 42X01",
	"ERROR: parser: parse error at or near",
	"ERROR:sssyntax error at or near",
	"exception",
	"Exception",
	"expected",
	"failed",
	"ibm_db_dbi",
	"IfxException",
	"Informix ODBC Driver",
	"Ingres SQLSTATE",
	"IngresW.Driver",
	"Invalid end of SQL statement",
	"Invalid keyword or missing delimiter",
        "Invalid argument",
	"io.crate.client.jdbc",
	"io.prestosql.jdbc",
	"JDBC Driver",
	"JET Database Engine",
	"macromedia.jdbc.oracle",
	"macromedia.jdbc.sqlserver",
	"MariaDB",
	"MemSQL",
	"Microsoft Access",
	"Microsoft SQL Native Client error",
	"MonetDBODBC Driver",
	"MySQL",
	"MySqlClient",
	"MySqlException",
	"MySQLSyntaxErrorException",
	"nl.cwi.monetdb.jdbc",
	"Npgsql",
	"ODBC Driver",
	"ODBC Informix driver",
	"ODBC Microsoft Access",
	"ODBC SQL Server Driver",
	"OLE DB",
	"Oracle.Driver",
	"Oracle error",
	"OracleException",
	"oracle.jdbc",
	"org.apache.derby",
	"org.firebirdsql.jdbc",
	"org.h2.jdbc",
	"org.hsqldb.jdbc",
	"org.jkiss.dbeaver.ext.vertica",
	"org.postgresql.jdbc",
	"org.postgresql.util.PSQLException",
	"org.sqlite.JDBC",
	"Pdo.",
	"PG::SyntaxError:",
	"PostgreSQL",
	"PostgreSQL query failed",
	"ProgrammingError",
	"PSQLException",
	"quoted string not properly terminated",
	"Semantic",
	"SQL command not properly ended",
	"SQL error",
	"sqlite",
	"SQL Server",
	"SQLSTATE",
	"SQL syntax",
	"Sybase.Data.AseClient",
	"Sybase message",
	"Sybase.Server message",
	"SybSQLException",
	"syntax",
	"Syntax",
	"Syntax error",
	"Syntax error or access violation",
	"System.Data.SqlClient.SqlException",
	"Transaction rollback",
	"unexpected",
	"Unexpected end of command in statement ",
	"Unexpected token",
	"UNION query has",
	"Unknown column",
	"valid MySQL result",
	"valid PostgreSQL result",
	"violation",
        "warning:",
	"weblogic.jdbc.informix",
	"your MySQL server version",
	"Zend_Db_"]
    for line in error_list:
        error = re.search(line, resp.text, re.IGNORECASE)
        if error:
            return line

# Perform the SQLi call for injection
def detect_sqli(url,headers,get_post,inj_param,params,prefix,inj_str):
    inj_params = dict()
    for param in params:
        inj_params[param] = def_str
        if param == inj_param:
            inj_params[param] = prefix + inj_str

    # Do GET or POST
    if get_post.lower() == "get":
        r = requests.get(url,params=inj_params,headers=headers,timeout=timeout,verify=False)
    elif get_post.lower() == "post":
        r = requests.post(url,data=inj_params,headers=headers,timeout=timeout,verify=False)
    
    # Pretty soup text and regex search
    s = BeautifulSoup(r.text, 'lxml')

    # Return the error if detected in text of response
    return detect_error(s)

# Main
def main(argv):
    if len(sys.argv) == 6:
        params = sys.argv[1].split(",")
        get_post = sys.argv[2]
        prefix = sys.argv[3]
        injlist_read = sys.argv[4]
        url = sys.argv[5]
    else:
        print("[*] Usage: " + sys.argv[0] + " <param1,param2,..> <get_or_post> <prefix> <file_injection_strings> <url>")
        print("[*] Example: " + sys.argv[0] + " id get \"1' \" /usr/share/wordlists/seclists/Fuzzing/SQLi/Generic-SQLi.txt http://192.168.252.6/cat.php\n")
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

        print("[*] Testing parameter \"" + inj_param + "\"")

        # Loop the strings in attempting to detect possible SQLi
        for inj_str in tqdm(inj_lines,total=len_inj_lines):
            inj_str = inj_str.strip('\n')
            ret_err = detect_sqli(url,headers,get_post,inj_param,params,prefix,inj_str)
            if ret_err:
                print("\n[*] String \"" + ret_err + "\" found in response for param \"" + inj_param + "\" using string \"" + prefix + inj_str + "\". Possible SQL injection found?")

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
