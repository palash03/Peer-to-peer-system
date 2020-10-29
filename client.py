import socket
import os
from _thread import *
import pickle
import random

s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s.connect((socket.gethostname(),7734))
print(f"Connected to {socket.gethostname()} with port 7734")

peerRfc = {} # The peers who have the RFC. Key: RFC number, Value: the list of peers having the RFC

clienthost = '127.0.0.1'
clientport = 20000 + random.randint(1,8000)

# RFC directory
currdir = os.listdir(os.getcwd()+'/RFC')
count = 0
for rfc in currdir:
    if rfc.startswith('.'):
        continue
    peerRfc[count] = str(rfc[:-4])
    count += 1
print(peerRfc)

def upload():
    sock = socket.socket()
    sock.bind((clienthost,clientport))
    sock.listen(5)
    while True:
        downloadSocket,downloadAddr = sock.accept()
        msgTransfer = downloadSocket.recv(1024)
        msg = pickle.loads(msgTransfer)
        print(msg)
        downloadSocket.send()   
        downloadSocket.close()

def addFileToClient(number,title):
    res = "ADD RFC " + str(number) + " P2P-CI/1.0\n"\
           "HOST: " + str(clienthost) + "\n"\
           "Port: " + str(clientport) + "\n"\
           "Title: " + str(title)
    return res

def getUserInput():
    print("Enter the function you want to perform: GET, LOOKUP, ADD, LIST, EXIT")
    inp = input()
    if inp == "ADD":
        print("Enter RFC number: ")
        rfcNum = input()
        print("Enter RFC Title: ")
        rfcTitle = input()
        directory = os.getcwd() + '/RFC/'
        print("Directory: " + str(directory))
        fileSelect = directory + str(rfcTitle) + ".txt"
        print("File: " + str(fileSelect))
        if os.path.isfile(fileSelect):
            data = addFileToClient(rfcNum,rfcTitle) 
            #data = str(data[2:])
            print(data)
            info = pickle.dumps(data)
            s.send(info)
            receive = s.recv(1024)
            print(receive)
        else:
            print("404 Error: File not found")
        getUserInput()

# Threads for managing download requests from peers which remains active until connection is open
start_new_thread(upload,())
getUserInput()