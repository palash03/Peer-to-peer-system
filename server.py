import socket
from _thread import *
import pickle
import platform
import time

def delAllMapping(hname):
    global rfcMapping, activePeer
    if activePeer[hname]:
        del activePeer[hname]
    for key,value in rfcMapping.items():
        hosts, title = value
        if hname in hosts:
            if len(hosts) == 1:
                del rfcMapping[key]
            else:
                hosts.remove(hname)
                rfcMapping[key] = (hosts,title)

def getResponseAdd(number,title,hname,port):
    return "P2P-CI/1.0 200 OK\n"+str(number)+" "+str(title)+" "+str(hname)+" "+str(port)

def getResponseLookup(number,title):
    global rfcMapping, activePeer
    print("Inside lookup response")
    print(rfcMapping)
    response = ""
    if number in rfcMapping:
        hosts, rfcTitle = rfcMapping[number]
        if len(hosts) > 0:
            response += "P2P-CI/1.0 200 OK"
            for h in hosts:
                getHostInfo = str(number) + " " + title + " " + str(h) + " " + str(activePeer.get(h))
                response += "\n" + getHostInfo
        #else:
            #response = "No peer has this RFC"
    else:
        response = "P2P-CI/1.0 404 Not Found"
    return response

def getResponseGet(number,title,check):
    sendResponse = []
    # case when rfc is present with the peer
    if check:
        hosts,rfcTitle = rfcMapping.get(number)
        sendResponse.append(hosts[0])
        sendResponse.append(activePeer[hosts[0]])
    else:
        t = time.localtime()
        current_time = time.strftime("%H:%M:%S", t)
        print(current_time)
        msg = "P2P-CI/1.0 404 Not Found\n"\
              "Date: " + str(current_time) + "\n"\
              "OS: " + str(platform.platform()) + "\n"
        sendResponse.append(msg)
    return sendResponse

def createMapping(number,title,hname):
    global rfcMapping, activePeer
    if number in rfcMapping:
        peerList, rfcTitle = rfcMapping[number]
        peerList.append(hname)
        rfcMapping[number] = (peerList,rfcTitle)
    else:
        peerList = [hname]
        rfcMapping[number] = (peerList,title)

def manageClientRequest(clientsocket,address):
    global activePeer, rfcMapping
    info = clientsocket.recv(1024)
    dataFromClient = pickle.loads(info)
    hname = dataFromClient[0]
    port = dataFromClient[1]
    print("The info list of peer for the client")    
    # Code for the mappings 
    activePeer[hname] = port
    for key,value in dataFromClient[2].items():
        if key not in rfcMapping:
            peer = [hname]
            rfcMapping[key] = (peer,value)
        else:
            peer,title = rfcMapping.get(key)
            peer.append(hname)
            rfcMapping[key] = (peer,title)
    print(rfcMapping)
    while True:
        response2 = clientsocket.recv(1024).decode('utf-8')
        print(response2)
        # case ADD
        if response2[0] == 'A':
            print("Inside ADD")
            # list of incoming file
            res = response2.split("\n")
            print(res)
            # 'ADD RFC 3 P2P-CI/1.0', 'HOST: 127.0.0.1', 'Port: 24520', 'Title: rfc0005'
            rfcNo = res[0][8]
            rfcTitle = res[3][7:]
            rfcHost = res[1][6:]
            #rfcPort = res[2][6:]
            createMapping(rfcNo,rfcTitle,rfcHost)
            print(rfcMapping)
            # P2P-CI/1.0 200 OK\n1 RFC001 127.0.0.2 61405
            sendResponse = getResponseAdd(res[0][8],res[3][7:],res[1][6:],res[2][6:])
            print(sendResponse)
            clientsocket.send(bytes("P2P-CI/1.0 200 OK \n" + rfcNo + "\n" + rfcTitle + "\n" + rfcHost + "\n",'utf-8'))

        # case LIST
        elif response2[0] == 'L' and response2[1] == 'I':
            break

        elif response2[0] == 'L' and response2[1] == 'O':
            res = response2.split("\n")
            rfcNo = (res[0].split())[1]
            rfcTitle = (res[3][7:])
            msg = getResponseLookup(rfcNo,rfcTitle)
            print(msg)
            clientsocket.send(bytes(msg,'utf-8'))
        
        # case GET
        elif response2[0] == 'G':
            res = response2.split("\n")
            print("Inside GET")
            print(res)
            rfcNo = res[1]
            rfcTitle = res[4]
            peerHasRfc = False
            if rfcNo in rfcMapping:
                peerHasRfc = True
            msg = getResponseGet(rfcNo,rfcTitle,peerHasRfc)
            msgList = pickle.dumps(msg,-1)
            clientsocket.send(msgList)

        # case EXIT
        elif response2[0] == 'E':
            break

    print("Closing connection with the client")
    # Remove all mappings for RFC and peer information
    delAllMapping(hname)
    clientsocket.close

def main():

    s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    s.bind((socket.gethostname(),7734))
    s.listen(5)

    print("Let's get this server rolling")

    while True:
        clientsocket, address = s.accept()
        print(f"A new connection has been established from {address}")
        #clientsocket.send(bytes("Let me in the server", "utf-8"))
        start_new_thread(manageClientRequest,(clientsocket,address))    
    clientsocket.close

rfcMapping = {} # Key: rfc number and Value is a tuple (list of peers using the rfc, title of rfc)
activePeer = {} # Key: host name and Value: port used for connection to server

if __name__ == "__main__":
    main()