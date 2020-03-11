from os import curdir, sep

class Controller(object):
    def __init__(self,csocket):
        self.csocket = csocket
        self.host, self.port = self.csocket.getpeername()

    def parseRequest(self):
        msgFromClient = self.readRequest(self.csocket)
        print(f"\nServer received the message:\n\n\n '{msgFromClient}' \n\n\nfrom {self.host} on port {self.port}\n\n\n")

        if not(self.checkMethod(msgFromClient)):
            self.sendMethodNotAllowed()
            self.closeConnection()

        elif self.isHomepageRequest(msgFromClient):
            self.sendHomepage()
            self.closeConnection()

        elif self.isPOSTRequest(msgFromClient):
            path = self.getPOSTpath(msgFromClient)
            try:
                self.gs = self.connectToGateway('localhost', 12000)
                self.forwardMsgToGateway(msgFromClient)
                ''' wait for the response from the gateway server '''
            except Exception:
                print('Connection to gateway failed. ')

        else:
            self.sendBadRequest()
            self.closeConnection()

    def readRequest(self, socket): #reads the message coming from the client
        rawData = socket.recv(4092)
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

    def closeConnection(self): #closes the TCP connection
        self.csocket.close()
        print(f'\nThe connection to {self.host} on port {self.port} has been closed by the server')

    def checkMethod(self, clientMsg):
        httpMethod = clientMsg.split()[0]
        if httpMethod == 'GET' or httpMethod == 'POST':
            return True
        return False

    def sendMethodNotAllowed(self):
        response_msg = 'HTTP/1.1 405 Method Not Allowed\n'
        self.writeResponse(self.csocket, response_msg)

    def sendBadRequest(self):
        response_msg = 'HTTP/1.1 400 Bad Request\n'
        self.writeResponse(self.csocket, response_msg)

    def isHomepageRequest(self, clientMsg):
        return clientMsg[0:3] == 'GET' and clientMsg[4] == '/'   #we gotta write also the case of /index.html


    def isPOSTRequest(self,clientMsg):
        return clientMsg[0:4] == 'POST'

    def getPOSTpath(self,clientMsg):
        path = clientMsg.split()[1]
        print(f"the path is {path}")
        return path

    def sendHomepage(self):
        page = self.readFile(curdir + '/index.html')
        response_msg = 'HTTP/1.1 200 OK\n\n' + page
        print(f"Message to send to the client as response:\n{response_msg}")
        self.writeResponse(self.csocket, response_msg)

    def connectToGateway(self, IP, PORT):
        # AF_INET means IPv4, SCOCK_STREM means TCP
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((IP, PORT))
        return s

    def forwardMsgToGateway(self, msg):
        self.writeResponse(self.gs, msg)
