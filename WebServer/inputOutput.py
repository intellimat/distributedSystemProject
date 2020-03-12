import socket

def readRequest(self, sock): #reads the message coming from the client
    rawData = sock.recv(4092)
    decodedData = rawData.decode("utf-8")
    return decodedData

def readFile(self, path): #reads a file stored in a directory specified by the path argument
    f = open(path)
    content = f.read()
    f.close()
    return content

def writeResponse(self, socket, data): #writes a response to the client
    socket.send(bytes(data,"utf-8"))
    print("\nResponse sent to the client. ")
