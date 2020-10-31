import socket
import os
from _thread import *
import pickle
import random

def upload(clienthost,clientport):
    print("Entering upload")
    host = '0.0.0.0'
    sock = socket.socket()
    sock.bind((host,clientport))
    sock.listen(5)
    while True:
        downloadSocket,downloadAddr = sock.accept()
        msgTransfer = downloadSocket.recv(1024)
        msg = pickle.loads(msgTransfer)
        print("Print the msg now....")
        print(msg)
        downloadSocket.send()   
        downloadSocket.close

def performAdd(clienthost,clientport,number,title):
    return "ADD RFC " + str(number) + " P2P-CI/1.0\n"\
           "HOST: " + str(clienthost) + "\n"\
           "Port: " + str(clientport) + "\n"\
           "Title: " + str(title)

def performLookup(host,port,number,title):
    return "LOOKUP " + str(number) + " P2P-CI/1.0" + "\n"\
            "Host: " + str(host) + "\n"\
            "Port: " + str(port) + "\n"\
            "Title: " + str(title)

def getUserInput(s,clienthost,clientport):
    print("Enter the function you want to perform: GET, LOOKUP, ADD, LIST, EXIT")
    inp = input()
    if inp == "ADD":
        print("Enter RFC number: ")
        rfcNum = input()
        print("Enter RFC Title: ")
        rfcTitle = input()
        directory = os.getcwd() + '/RFC/'
        fileSelect = directory + str(rfcNum) + "-" + str(rfcTitle) + ".txt"
        if os.path.isfile(fileSelect):
            data = performAdd(clienthost,clientport,rfcNum,rfcTitle) 
            #print(data)
            #info = pickle.dumps(bytes(data))
            s.send(bytes(data,'utf-8'))
            print("ADD response from server is: ")
            receive = s.recv(1024)
            print(receive)
        else:
            print("404 Error: File not found")
        getUserInput(s,clienthost,clientport)
    
    elif inp == "LOOKUP":
        print("Enter RFC number: ")
        rfcNum = input()
        print("Enter RFC Title: ")
        rfcTitle = input()          
        getRfcDetails = performLookup(clienthost,clientport,rfcNum,rfcTitle)
        print(getRfcDetails)
        s.send(bytes(getRfcDetails,'utf-8'))
        response = s.recv(1024)
        print(response)
        getUserInput(s,clienthost,clientport)
    
    elif inp == "EXIT":
        s.send(bytes("EXIT",'utf-8'))
        s.close

def main():
    s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    s.connect((socket.gethostname(),7734))
    print(f"Connected to {socket.gethostname()} with port 7734")

    peerRfc = {} # The peers who have the RFC. Key: RFC number, Value: the list of peers having the RFC

    clienthost = '127.0.0.1'
    clientport = 20000 + random.randint(1,8000)

    # RFC directory create ADD request for new peer
    currdir = os.listdir(os.getcwd()+'/RFC')
    for rfc in currdir:
        if rfc.startswith('.'):
            continue
        file = rfc.split('-')
        peerRfc[file[0]] = str(file[1])
    print(peerRfc)
    details = ""
    for key,value in peerRfc.items():
        details += "ADD " + str(key) + " P2P-CI/1.0\n"\
                "Host: " + str(clienthost)+ "\n"\
                "Port: " + str(clientport)+ "\n"\
                "Title: " + str(value) + "\n"
    sendToServer = [clienthost,clientport,peerRfc,details]
    sendData = pickle.dumps(sendToServer,-1)
    s.send(sendData)
    s.close
    # Threads for managing download requests from peers which remains active until connection is open
    start_new_thread(upload,(clienthost,clientport))
    getUserInput(s,clienthost,clientport)

if __name__ == "__main__":
    main()