import socket
import os
from _thread import *
import pickle
import random

s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s.connect((socket.gethostname(),7734))
print(f"Connected to {socket.gethostname()} with port 7734")

peerRfc = {} # The peers who have the RFC. Key: RFC number, Value: the list of peers having the RFC

clienthost = s.getsockname()[0]
clientport = 20000 + random.randint(1,8000)
print(clienthost)

# RFC directory
currdir = os.listdir(os.getcwd()+'/RFC')
count = 0
for rfc in currdir:
    if rfc.startswith('.'):
        continue
    peerRfc[count] = str(rfc[:-4])
    count += 1
print(peerRfc)
msg = ""
while True:
    m = s.recv(1024)   
print(m.decode('utf-8'))

def upload():
    sock = socket.socket()
    sock.bind((clienthost,clientport))
    sock.listen(5)
    while True:
        downloadSocket,downloadAddr = sock.accept()
        msgTransfer = downloadSocket.recv(1024)
        msg = pickle.loads(msgTransfer)
        print(msg)

def input_type():
    print("Enter the function you want to perform: GET, LOOKUP, ADD, LIST, EXIT")
    in = input()
    if in == "ADD":
        

start_new_thread(upload,())
input_type()
