import socket
import os
import sys
from _thread import *
import pickle
import random
import platform
import time

def upload(clienthost,clientport):
    host = '0.0.0.0'
    sock = socket.socket()
    sock.bind((host,clientport))
    sock.listen(5)
    while True:
        downloadSocket,downloadAddr = sock.accept()
        msgTransfer = downloadSocket.recv(1048576)
        msg = pickle.loads(msgTransfer)
        print("Print the msg now....")
        # ['GET 1 P2P-CI/1.0\nHost: 127.0.0.1\nOS: macOS-10.15.7-x86_64-i386-64bit', 'rfc0001']
        reply = ""
        message = msg[0]
        print("Entering transfer mode ....inside upload******")
        print(msg)
        t = time.localtime()
        current_time = time.strftime("%H:%M:%S", t)
        print("Testing 1")
        print(message)
        if "GET" in message and "Host" in message and "OS" in message:
            if "P2P-CI/1.0" not in message:
                reply += "ERROR 505: P2P-CI/1.0 version not supported" 
            else:
                breakContent = message.split("\n")
                if "GET" in breakContent[0]:
                    rfcNo = breakContent[0][4]
                    filePath = os.getcwd() + '/RFC/' + str(rfcNo) + "-" + str(msg[1]) + ".txt"
                    fileContent = ""
                    with open(filePath,'r') as f:
                        fileContent = f.read()
                    reply += "P2P-CI/1.0 200OK\n"\
                             "Date: " + str(current_time) + "\n"\
                             "OS: " + str(platform.platform()) + "\n"\
                             "Last-Modified: " + str(time.ctime(os.path.getmtime(filePath))) + "\n"\
                             "Content-Length: " + str(len(fileContent)) + "\n"\
                             "Content-Type: text/plain\n"
                    reply += str(fileContent)
                    print("File Transfer Completed...")
                else:
                    print("Incorrect request to accomodate")
        downloadSocket.sendall(bytes(reply,'utf-8'))
        downloadSocket.close

def performAdd(clienthost,clientport,number,title):
    return "ADD RFC " + str(number) + " P2P-CI/1.0\n"\
           "HOST: " + str(clienthost) + "\n"\
           "Port: " + str(clientport) + "\n"\
           "Title: " + str(title)

def transferFile(number, title, request):
    print(request)
    hname = request[0]
    port = int(request[1])
    s = socket.socket()
    s.connect((hname,port))
    msg = "GET " + str(number) + " P2P-CI/1.0\n"\
          "Host: " + str(hname) + "\n"\
          "OS: " + str(platform.platform())
    msgList = [msg,title]
    m = pickle.dumps(msgList,-1)
    s.send(m)
    print("********Getting data from the peer*********")
    res = s.recv(1048576)
    if len(str(res)) > 0:
        directory = os.getcwd() + "/RFC/Downloaded" + str(number) + ".txt"
        with open(directory,'w') as f:
            f.write(str(res.decode('utf-8')))
        print("File is stored in the new directory now")
    print(res)

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
            s.send(bytes(data,'utf-8'))
            print("ADD response from server is: ")
            receive = s.recv(1024)
            print(receive)
        else:
            print("404 Error: File not found")
        getUserInput(s,clienthost,clientport)
    
    elif inp == "LIST":
        res = "LIST ALL P2P-CI/1.0\n"\
              "Host: " + str(clienthost) + "\n"\
              "Port: " + str(clientport)
        print(res)
        s.send(bytes(res,'utf-8'))
        getList = s.recv(4096)
        print(getList)
        getUserInput(s,clienthost,clientport)

    elif inp == "GET":
        print("Enter RFC number: ")
        rfcNum = input()
        print("Enter RFC Title: ")
        rfcTitle = input()
        request = "GET\n" + str(rfcNum) + "\n" + str(clienthost) + "\n" + str(clientport) + "\n" + str(rfcTitle)
        s.send(bytes(request,'utf-8'))
        #s.send(pickle.dumps(request,-1)) 
        res = s.recv(1024)
        resList = pickle.loads(res)
        if len(resList) > 1:
            transferFile(rfcNum,rfcTitle,resList)
            sendInfoToServer = "GET Request Completed\n" + "RFC: " + str(rfcNum) + "\n" + "Title: " + str(rfcTitle) + "\n" + "Host: " + str(clienthost)
            s.send(bytes(sendInfoToServer,'utf-8'))
        else:
            print(resList)
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
    clienthost = sys.argv[1]
    clientport = 60000 + random.randint(1,1000)
    print(f"Client port {clientport}")
    currdir = os.listdir(os.getcwd()+'/RFC')
    details = ""
    sendToServer = [clienthost,clientport,peerRfc,details]
    sendData = pickle.dumps(sendToServer,-1)
    s.send(sendData)
    s.close
    # Threads for managing download requests from peers which remains active until connection is open
    start_new_thread(upload,(clienthost,clientport))
    getUserInput(s,clienthost,clientport)

if __name__ == "__main__":
    main()