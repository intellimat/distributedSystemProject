import os
import sys
import socket

pathRepo = os.path.dirname(os.path.dirname(os.getcwd()))
sys.path.insert(1, pathRepo)

from distributedSystemProject.utils import inputOutput as io

class Controller(object):
    def __init__(self,csocket):
        self.csocket = csocket
        self.host, self.port = self.csocket.getpeername()

    def parseRequest(self):
        msgFromClient = io.readRequest(self.csocket)
        print(f"\nServer received the message:\n\n\n '{msgFromClient}' \n\n\nfrom {self.host} on port {self.port}\n\n\n")

        if not(self.checkMethod(msgFromClient)):
            self.sendMethodNotAllowed()
            io.closeConnection(self.csocket)

        elif self.isFaviconRequest(msgFromClient):
            self.sendFavicon()
            io.closeConnection(self.csocket)

        elif self.isHomepageRequest(msgFromClient):
            self.sendHomepage()
            io.closeConnection(self.csocket)

        elif self.isPOSTRequest(msgFromClient):
            self.handlePOSTrequest(msgFromClient)

        else:
            self.sendBadRequest()
            io.closeConnection(self.csocket)

    def checkMethod(self, clientMsg):
        httpMethod = clientMsg.split()[0]
        if httpMethod == 'GET' or httpMethod == 'POST':
            return True
        return False

    def sendMethodNotAllowed(self):
        s = io.setCode('HTTP/1.1', 405)
        s = io.setResponseAnswer(s, 'Method Not Allowed\n')
        s = io.setConnection(s, 'Close')
        io.writeResponse(self.csocket, s)

    def sendBadRequest(self):
        s = io.setCode('HTTP/1.1', 400)
        s = io.setResponseAnswer(s, 'Bad Request\n')
        s = io.setConnection(s, 'Close')
        io.writeResponse(self.csocket, s)

    def isHomepageRequest(self, clientMsg):
        return clientMsg[0:3] == 'GET' and clientMsg[4] == '/'   #we gotta write also the case of /index.html

    def isFaviconRequest(self, msgFromClient):
        print('Checking if is favicon request \n')
        arguments = msgFromClient.split()
        httpMethod = arguments[0]
        path = arguments[1]
        return httpMethod == 'GET' and path == '/favicon.ico'

    def isPOSTRequest(self,clientMsg):
        return clientMsg[0:4] == 'POST'

    def getPOSTpath(self,clientMsg):
        path = clientMsg.split()[1]
        print(f"the path is {path}")
        return path

    def sendHomepage(self):
        page = io.readFile(os.curdir + '/index.html')
        pageLength = len(page)
        # s is the response message
        s = io.setCode('HTTP/1.1', 200)
        s = io.setResponseAnswer(s, 'OK')
        s = io.setContentLength(s, pageLength)
        s = io.setContentType(s, 'text/html')
        s = io.setConnection(s, 'Close')
        s = s + f'\n\n{page}'
        print(f"Message to send to the client as response: \n\n HTML page")
        io.writeResponse(self.csocket, s)

    def sendFavicon(self):
        favicon = io.readFile(os.curdir + '/favicon.ico')
        faviconLength = len(favicon)
        # s is the response message
        s = io.setCode('HTTP/1.1', 200)
        s = io.setResponseAnswer(s, 'OK')
        s = io.setContentLength(s, faviconLength)
        s = io.setContentType(s, 'image/x-icon')
        s = io.setConnection(s, 'Close')
        s = s + f'\n\n{favicon}'
        print(f"Message to send to the client as response: favicon ")
        io.writeResponse(self.csocket, s)

    def connectToGateway(self, IP, PORT):
        # AF_INET means IPv4, SCOCK_STREM means TCP
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((IP, PORT))
        return s

    def forwardMsgToGateway(self, msg):
        io.writeResponse(self.gs, msg)

    def handlePOSTrequest(self, msgFromClient):
        #path = self.getPOSTpath(msgFromClient)
        try:
            print('Trying to connect to the gateway server.')
            self.gs = self.connectToGateway('localhost', 12000)
            print('\nConnected to the gateway.')
            self.forwardMsgToGateway(msgFromClient)
            #gatewayResponse = io.readRequest(self.gs)
            #print(f'\n\nThe response from the gateway is: "{gatewayResponse}" \n\n')
            'Here goes all the logic to manage the response from the gateway server'
            'we need to wait for the gateway to process the request but for now we send an ok 200 to the client'
            s = io.setCode('HTTP/1.1', 200)
            s = io.setResponseAnswer(s, 'OK')
            s = io.setContentLength(s, 0)
            s = io.setConnection(s, 'Close\n\n')
            io.writeResponse(self.csocket, s)
            print(f'Sent \n{s} to the client after POST request')
            io.closeConnection(self.csocket)
        except socket.error as exc:
            print('Connection to gateway failed. ')
            s = io.setCode('HTTP/1.1', 500)
            s = io.setResponseAnswer(s, 'Internal Server Error')
            s = io.setConnection(s, 'Close\n\n')
            s = s + 'Socket error: Connection to the gateway failed. \n'
            io.writeResponse(self.csocket, s)
            print(f'Sent \n{s} to the client after POST request\n')
            io.closeConnection(self.csocket)
