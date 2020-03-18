''' Helper module '''

def readRequest(sock): #reads the message coming from the client
    rawData = sock.recv(4092)
    decodedData = rawData.decode("utf-8")
    return decodedData

def readFile(path): #reads a file stored in a directory specified by the path argument
    f = open(path)
    content = f.read()
    f.close()
    return content

def writeResponse(sock, data): #writes a response to the client
    sock.send(bytes(data,"utf-8"))
    print("\nResponse sent. ")
