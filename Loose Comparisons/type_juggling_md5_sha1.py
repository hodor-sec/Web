#!/usr/bin/python3
import re
import hashlib
import string
import itertools
import os
import sys
import codecs

# Handle CTRL-C
def keyboard_interrupt():
    """Handles keyboardinterrupt exceptions"""
    print("\n\n[*] User requested an interrupt, exiting...")
    exit(0)

def gen_checksum(hashtype):
    count = 0
    if hashtype == "sha1":
        for word in map(''.join, itertools.product(string.printable, repeat=int(32))):
            sha1 = hashlib.sha1(word.encode('utf-8')).hexdigest()
            print("[*] Attempting " + hashtype.upper() + ": " + sha1,end='\r')
            if re.match(r'0+[eE]\d+$', sha1):
                print("[+] Found a valid string! " + word)
                print("[+] Requests made: " + str(count))
                print("[+] Equivalent loose comparison: " + sha1 + " == 0\n")
                return sha1
            count += 1
    elif hashtype == "md5":
        for word in map(''.join, itertools.product(string.printable, repeat=int(40))):
            md5 = hashlib.md5(word.encode('utf-8')).hexdigest()
            print("[*] Attempting " + hashtype.upper() + ": " + md5,end='\r')
            if re.match(r'0+[eE]\d+$', md5):
                print("[+] Found a valid string! " + word)
                print("[+] Requests made: " + str(count))
                print("[+] Equivalent loose comparison: " + md5 + " == 0\n")
                return md5
            count += 1
    else:
        print("[!] Error: invalid hashtype\n")
        exit(-1)

# Main
def main(argv):
    if len(sys.argv) == 2:
        hashtype = sys.argv[1]
    else:
        print("[*] Usage: " + sys.argv[0] + " <hashtype>")
        print("[*] Example: " + sys.argv[0] + " md5\n")
        exit(0)

    # Do stuff
    try:
        gen_checksum(hashtype)
    except KeyboardInterrupt:
        keyboard_interrupt()

# If we were called as a program, go execute the main function.
if __name__ == "__main__":
    main(sys.argv[1:])
