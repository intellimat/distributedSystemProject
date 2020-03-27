''' Helper module '''
import socket
import json

def readMessage(sock): #reads the message coming from the client
    rawData = sock.recv(4092)
    decodedData = rawData.decode("utf-8")
    host, port = sock.getpeername()
    print(f"Received the message:\n'{decodedData}' \nfrom {host} on port {port}\n\n")
    return decodedData

def readFile(path): #reads a file stored in a directory specified by the path argument
    f = open(path)
    content = f.read()
    f.close()
    print(f'\nRead file:\n{content}\n\n')
    return content

def writeMessage(sock, data): #writes a response to the client
    sock.send(bytes(data,"utf-8"))
    print(f'Sent:\n{data}\n')

def setContentLength(msg, msgLength):
    return msg + f'\nContent-Length: {msgLength}'

def setContentType(msg, type):
    return msg + f'\nContent-Type: {type}'

def setConnection(msg, connection):
    return msg + f'\nConnection: {connection}'

def setCode(msg, code):
    return msg + f' {str(code)}'

def setMessageAnswer(msg, answer):
    return msg + f' {answer}'

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
    counter = 1
    while response != '<ACK>' and counter<3:
        counter += 1
        writeMessage(sock,'<ENQ>')
        response = readMessage(sock)
    if response != '<ACK>':
        raise Exception(f'Impossible to establish connection with {address}')
    print(f'Connection to {address} established. ')
    return sock

def connectTo(IP, PORT):
    # AF_INET means IPv4, SCOCK_STREM means TCP
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((IP, PORT))
    return s
