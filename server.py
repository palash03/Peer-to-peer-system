import socket
from _thread import *
import pickle

s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s.bind((socket.gethostname(),7734))
s.listen(5)

print("Let's get this server rolling")

rfcMapping = {} # Key: rfc number and Value is a tuple (list of peers using the rfc, title of rfc)
activePeer = {} # Key: host name and Value: port used for connection to server

def manageClientRequest(clientsocket,address):
    global activePeer, rfcMapping
    info = clientsocket.recv(1024)
    dataFromClient = pickle.loads(info)
    print(dataFromClient)

    # Need to write code for the mappings 


    while True:
        if dataFromClient[0] == 'A':
            # list of incoming file
            res = dataFromClient.split("\n")
            # 'ADD RFC 3 P2P-CI/1.0', 'HOST: 127.0.0.1', 'Port: 24520', 'Title: rfc0005'
            textNeeded = res[0][8] + " " + res[3][7:] + " " + res[1][6:] + " " + res[2][6:]
            print(textNeeded)
            #3 RFC003 127.0.0.2 60234
            break

        elif dataFromClient[0] == 'E':
            break

    print("Closing connection with the client")
    clientsocket.close()

while True:
    clientsocket, address = s.accept()
    print(f"A new connection has been established from {address}")
    #clientsocket.send(bytes("Let me in the server", "utf-8"))
    start_new_thread(manageClientRequest,(clientsocket,address))    
clientsocket.close()