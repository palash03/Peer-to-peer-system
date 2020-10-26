import socket
import os
from _thread import *
import pickle
import sys

s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s.connect((socket.gethostname(),7734))
print(sys.argv)
# RFC directory
currdir = os.listdir(os.getcwd()+'/RFC')
#print(currdir)
#for rfc in currdir:
#    print(rfc)

msg = ""
while True:
    m = s.recv(1024)   
print(m.decode('utf-8'))
