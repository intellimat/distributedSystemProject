''' Helper module '''
import socket
import os
import sys
pathRepo = os.path.dirname(os.path.dirname(os.getcwd()))
sys.path.insert(1, pathRepo)

from distributedSystemProject.utils import stringManager as sm
from distributedSystemProject.utils.Exception import NetworkException


def readMessage(sock): #reads the message coming from the client
    rawData = sock.recv(8192)
    decodedData = rawData.decode("utf-8")
    host, port = sock.getpeername()
    print(f"Received the message:\n'{decodedData}' \nfrom {host} on port {port}\n\n")
    return decodedData

def readFile(path): #reads a file stored in a directory specified by the path argument
    f = open(path)
    content = f.read()
    f.close()
    if len(content) < 100:
        print(f'\nRead file:\n{content}\n\n')
    return content

def writeFile(path, content):
    f = open(path, 'w')
    f.write(content)
    f.close()
    print(f'Written file with this content:\n {content}')


def writeMessage(sock, data): #writes a response to the client
    host, port = sock.getpeername()
    sock.send(bytes(data,"utf-8"))
    print(f'Sent:\n{data} to {host} on port {port}\n')


def closeConnection(socket): #closes the TCP connection
    host, port = socket.getpeername()
    socket.close()
    print(f'\nThe connection to {host} on port {port} has been closed by the server')

def establishConnection(address):
    print(f'Trying to connect to {address}\n')
    IP = address[0]
    PORT = address[1]
    sock = connectTo(IP, PORT)
    writeMessage(sock,'<ENQ>')
    response = readMessage(sock)
    counter = 0
    while response != '<ACK>' and counter<3:
        counter += 1
        writeMessage(sock,'<ENQ>')
        response = readMessage(sock)
    if response != '<ACK>':
        raise NetworkException(f'Impossible to establish connection with {address}')
    print(f'Connection to {address} established. ')
    return sock


def connectTo(IP, PORT):
    # AF_INET means IPv4, SCOCK_STREM means TCP
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((IP, PORT))
        return s
    except socket.error as e:
        raise NetworkException(f'impossible to connect through the socket system to the address: {IP} on port: {PORT}')
