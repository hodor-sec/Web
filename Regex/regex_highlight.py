#!/usr/bin/env python3
#
# Created by: hodorsec
# Description: Used for analyzing directories containing code or files, searching for a specific regex and highlighting the hits per file and line
# Version: 0.8.1
#
import sys
import re
import os
import glob
import argparse
from colorama import Fore, Style

# Color vars
clr_file = Fore.BLUE
clr_match = Fore.RED
clr_reset = Fore.RESET

# Highlight the text via regex
def highlight_text(color,line,pat,ign_case):
    if ign_case:
        if re.search(rf'({pat})',line,flags=re.IGNORECASE):
            return re.sub(rf'({pat})',color + r'\1' + clr_reset,line,flags=re.IGNORECASE).rstrip()
    else:
        if re.search(rf'({pat})',line):
            return re.sub(rf'({pat})',color + r'\1' + clr_reset,line).rstrip()

# Main
if __name__ == '__main__':
    # Check for given arguments
    parser = argparse.ArgumentParser(description='Regex search tool')
    parser.add_argument("--igncase", "-i", type=str, required=False, help="Ignore case sensitivity, enter any argument.")
    parser.add_argument("--pattern", "-p", type=str, required=True, help="The regex pattern to search for.")
    parser.add_argument("--dir", "-d", type=str, required=True, help="The directory to search in.")
    parser.add_argument("--ext", "-e", type=str, required=False, help="The file extension to search for.")

    # Check for any argument, else print help
    args = parser.parse_args()

    # Extract argument variables
    ign_case = args.igncase
    pattern = args.pattern
    directory = args.dir
    if args.ext:
        ext = "." + args.ext
    else:
        ext = ""

    # Use globbing for globbering through directories and files, alphabetically sorted
    for fn in sorted(glob.iglob(directory + "/**" + ext,recursive=True),key=str.casefold):
        if os.path.isfile(fn):
            try:
                with open(fn,'r') as f:
                    lines = f.readlines()

                # Initialize count variable for lines starting at 1 instead of 0
                count = 1

                # Do the regex matching
                for line in lines:
                    matched = highlight_text(clr_match,line,pattern,ign_case)
                    if matched:
                        # Dirty hack to work around directory "./" prefix
                        if directory == ".":
                            print(clr_file + fn[2:] + clr_reset + ":" + str(count) + ":" + matched)
                        else:
                            print(clr_file + fn[0:] + clr_reset + ":" + str(count) + ":" + matched)
                    count += 1
            except KeyboardInterrupt:
                print("\n\n[!] User requested an interrupt, exiting...\n")
                exit(0)
            except:
                pass





