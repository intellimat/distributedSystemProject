from os import curdir, sep

class Controller(object):
    def __init__(self,csocket):
        self.csocket = csocket
        self.host, self.port = self.csocket.getpeername()

    def parseRequest(self):
        msgFromClient = self.readRequest()
        print(f"\nServer received the message:\n\n\n '{msgFromClient}' \n\n\nfrom {self.host} on port {self.port}\n\n\n")

        ''' here goes all the logic of the gateway server '''

    def readRequest(self): #reads the message coming from the client
        rawData = self.csocket.recv(4092)
        decodedData = rawData.decode("utf-8")
        return decodedData

    def readFile(self, path): #reads a file stored in a directory specified by the path argument
        f = open(path)
        content = f.read()
        f.close()
        return content

    def writeResponse(self, data): #writes a response to the client
        self.csocket.send(bytes(data,"utf-8"))
        print("\nResponse sent to the client. ")

    def closeConnection(self): #closes the TCP connection
        self.csocket.close()
        print(f'\nThe connection to {self.host} on port {self.port} has been closed by the server')


    def sendMethodNotAllowed(self):
        response_msg = 'HTTP/1.1 405 Method Not Allowed\n'
        self.writeResponse(response_msg)

    def sendBadRequest(self):
        response_msg = 'HTTP/1.1 400 Bad Request\n'
        self.writeResponse(response_msg)

    def isPOSTRequest(self,clientMsg):
        return clientMsg[0:4] == 'POST'

    def getPOSTpath(self,clientMsg):
        path = clientMsg.split()[1]
        print(f"the path is {path}")
        return path
