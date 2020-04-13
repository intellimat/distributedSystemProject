''' Helper module '''
import socket
import os
import sys

pathRepo = os.path.dirname(os.path.dirname(os.getcwd()))
sys.path.insert(1, pathRepo)

from distributedSystemProject.utils import stringManager as sm
from distributedSystemProject.utils.Exception import NetworkException


def readMessage(socket): #reads the message coming from the client
    rawData = socket.recv(8192)
    decodedData = rawData.decode("utf-8")
    host, port = socket.getpeername()
    print(f"Received the message:\n'{decodedData}' \nfrom {host} on port {port}\n\n")
    return decodedData

def readFile(path): #reads a file stored in a directory specified by the path argument
    f = open(path)
    content = f.read()
    f.close()
    if len(content) < 100:
        print(f'\nRead file:\n{content}\n\n')
    else:
        print('Read a large file. ')
    return content

def writeFile(path, content):   #write a file in the directory specified byt the path argument
    f = open(path, 'w')
    f.write(content)
    f.close()
    print(f'Written file with this content:\n {content}')


def writeMessage(socket, data): #writes a message on a given socket
    host, port = socket.getpeername()
    socket.send(bytes(data,"utf-8"))
    if len(data)<500:
        print(f'Sent:\n{data} to {host} on port {port}\n')
    else:
        print(f'Sent a large quantity of data to {host} on port {port}')


def closeConnection(socket): #closes a TCP connection reachable through the socket argument
    host, port = socket.getpeername()
    socket.close()
    print(f'\nThe connection to {host} on port {port} has been closed by the server')

def establishConnection(address): #establish a connection that respects the protocol implemented
    print(f'Trying to connect to {address}\n')
    IP = address[0]
    PORT = address[1]
    socket = connectTo(IP, PORT)
    writeMessage(socket,'<ENQ>')
    response = readMessage(socket)
    counter = 0
    while response != '<ACK>' and counter<3:
        counter += 1
        writeMessage(socket,'<ENQ>')
        response = readMessage(socket)
    if response != '<ACK>':
        raise NetworkException(f'Impossible to establish connection with {address}')
    print(f'Connection to {address} established. ')
    return socket


def connectTo(IP, PORT): #tries to reach a server running on IP and PORT specified
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((IP, PORT))
        return s
    except socket.error as e:
        raise NetworkException(f'impossible to connect through the socket system to the address: {IP} on port: {PORT}')
