''' Helper module '''

def readMessage(sock): #reads the message coming from the client
    rawData = sock.recv(4092)
    decodedData = rawData.decode("utf-8")
    return decodedData

def readFile(path): #reads a file stored in a directory specified by the path argument
    f = open(path)
    content = f.read()
    f.close()
    return content

def writeMessage(sock, data): #writes a response to the client
    sock.send(bytes(data,"utf-8"))
    print("\nMessage sent. ")

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
