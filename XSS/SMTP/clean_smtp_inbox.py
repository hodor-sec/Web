#!/usr/bin/python3
import imaplib,sys

# Check args
if len(sys.argv) != 4:
    print("[*] Usage: " + sys.argv[0] + " <target> <imap_port> <mailbox>")
    print("[*] Example: " + sys.argv[0] + " mailserver 143 someone@nowhere.local\n")
    sys.exit(0)

# Variables
host = sys.argv[1]
imap_port = sys.argv[2]
mailbox = sys.argv[3]
password = input("Pasword: ")

# Perform connect and search for inbox
try:
    box = imaplib.IMAP4(host,imap_port)
    box.login(mailbox,password)
    box.select("Inbox")
except:
    print("[!] Error when attempting to connect. Wrong credentials?\n")
    exit(-1)

# Attempt to delete
print("[*] Attempting to delete inbox for mailbox " + mailbox + " on host " + host + ":" + str(imap_port) + "...")
try:
    typ,data = box.search(None, 'ALL')
    for num in data[0].split():
        box.store(num, '+FLAGS', '\\Deleted')

    # Cleanup
    box.expunge()
    box.close()
    box.logout()
    
    print("[+] Cleaned mailbox!\n")
except:
    print("[!] Something went wrong, check request.\n")
    exit(-1)


