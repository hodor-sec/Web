# Created by: hodorsec
# Description:
# Used for analyzing directories containing code or files, searching for a specific regex and highlighting the hits per file and line
#
#!/usr/bin/env python3
import sys
import re
import os
import glob
from colorama import Fore, Style

# Color vars
clr_file = Fore.GREEN
clr_match = Fore.RED
clr_reset = Fore.RESET

# Highlight the text via regex
def highlight_text(color,line,pat,ign_case):
    if ign_case == '1':
        if re.search(rf'({pat})',line,flags=re.IGNORECASE):
            return re.sub(rf'({pat})',color + r'\1' + clr_reset,line,flags=re.IGNORECASE).rstrip()
    else:
        if re.search(rf'({pat})',line):
            return re.sub(rf'({pat})',color + r'\1' + clr_reset,line).rstrip()

# Main
if __name__ == '__main__':
    # Check for given arguments
    if len(sys.argv) == 4:
        ign_case = sys.argv[1]
        pat = sys.argv[2]
        dir_file = sys.argv[3]
    else:
        print("[*] Usage: " + sys.argv[0] + " <ign_case> <pattern> <dir_to_search>")
        print("[*] Example: " + sys.argv[0] + " 0 passw /etc")
        print("[*] Example: " + sys.argv[0] + " 1 '.*test$' srcdir/files\n")
        exit(0)

    # Use globbing for globbering through directories and files, alphabetically sorted
    for fn in sorted(glob.iglob(dir_file + "/**",recursive=True),key=str.casefold):
        if os.path.isfile(fn):
            try:
                with open(fn,'r') as f:
                    lines = f.readlines()

                # Initialize count variable for lines starting at 1 instead of 0
                count = 1

                # Do the regex matching
                for line in lines:
                    matched = highlight_text(clr_match,line,pat,ign_case)
                    if matched:
                        print(clr_file + fn + clr_reset + ":" + str(count) + ":" + matched)
                    count += 1
            except KeyboardInterrupt:
                print("\n\n[!] User requested an interrupt, exiting...\n")
                exit(0)
            except:
                pass





