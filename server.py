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
    dataFromClient = pickle.loads(clientsocket.recv(1024))
    print(dataFromClient)

while True:
    clientsocket, address = s.accept()
    print(f"A new connection has been established from {address}")
    #clientsocket.send(bytes("Let me in the server", "utf-8"))
    start_new_thread(manageClientRequest,(clientsocket,address))    
clientsocket.close()