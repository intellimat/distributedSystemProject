import os
import sys
import socket
import json

pathRepo = os.path.dirname(os.path.dirname(os.getcwd()))
sys.path.insert(1, pathRepo)

from distributedSystemProject.utils import inputOutput as io
from distributedSystemProject.utils import stringManager as sm

class Controller(object):
    def __init__(self,csocket):
        self.csocket = csocket
        self.host, self.port = self.csocket.getpeername()

    def parseRequest(self):
        msgFromClient = io.readMessage(self.csocket)

        if not(self.checkMethod(msgFromClient)):
            self.sendMethodNotAllowed()
            io.closeConnection(self.csocket)

        elif self.isFaviconRequest(msgFromClient):
            self.sendFavicon()
            io.closeConnection(self.csocket)

        elif self.isGatewayRequest(msgFromClient):
            self.handleGatewayRequest(msgFromClient)
            #the connection will be closed by the handleGatewayRequest method

        elif self.isHomepageRequest(msgFromClient):
            self.sendHomepage()
            io.closeConnection(self.csocket)


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
        s = io.setMessageAnswer(s, 'Method Not Allowed\n')
        s = io.setConnection(s, 'Close')
        io.writeMessage(self.csocket, s)

    def sendBadRequest(self):
        s = io.setCode('HTTP/1.1', 400)
        s = io.setMessageAnswer(s, 'Bad Request\n')
        s = io.setConnection(s, 'Close')
        io.writeMessage(self.csocket, s)

    def isHomepageRequest(self, clientMsg):
        return clientMsg[0:3] == 'GET' and clientMsg[4] == '/'   #we gotta write also the case of /index.html

    def isFaviconRequest(self, msgFromClient):
        print('Checking if is favicon request. \n')
        arguments = msgFromClient.split()
        httpMethod = arguments[0]
        path = arguments[1]
        return httpMethod == 'GET' and path == '/favicon.ico'

    def isGatewayRequest(self,clientMsg):
        print('Checking if is gateway request. \n')
        path = self.getPath(clientMsg)
        basicPath = path.split('/')[1]
        return basicPath == 'gatewaySD'

    def getPath(self,clientMsg):
        path = clientMsg.split()[1]
        print(f"The path is: {path}\n")
        return path

    def sendHomepage(self):
        page = io.readFile(os.curdir + '/index.html')
        pageLength = len(page)
        # s is the response message
        s = io.setCode('HTTP/1.1', 200)
        s = io.setMessageAnswer(s, 'OK')
        s = io.setContentLength(s, pageLength)
        s = io.setContentType(s, 'text/html')
        s = io.setConnection(s, 'Close')
        s = s + f'\n\n{page}'
        print(f"Message to send to the client (user in this case) as response: \n\n HTML page")
        io.writeMessage(self.csocket, s)

    def sendFavicon(self):
        favicon = io.readFile(os.curdir + '/favicon.ico')
        faviconLength = len(favicon)
        # s is the response message
        s = io.setCode('HTTP/1.1', 200)
        s = io.setMessageAnswer(s, 'OK')
        s = io.setContentLength(s, faviconLength)
        s = io.setContentType(s, 'image/x-icon')
        s = io.setConnection(s, 'Close')
        s = s + f'\n\n{favicon}'
        print(f"Message to send to the client as response: favicon ")
        io.writeMessage(self.csocket, s)

    def sendDataAuth(self, sock, msgFromClient):
        body = msgFromClient.split('\r\n\r\n')[1]
        data = sm.getJSONobjectFromString(body)
        name = data.get('name')
        surname = data.get('surname')
        cardNumber = data.get('cardNumber')
        cvv = data.get('cvv')
        expDate = data.get('expDate')
        amount = data.get('amount')
        completeName = name + surname
        s = f'1#{completeName}#{cardNumber}#{amount}#{cvv}#{expDate}'
        lrc = sm.getLRCvalueFromString(s)
        s = '<STX>' + s + '<ETX>' + str(lrc)
        io.writeMessage(sock, s)

    def manageAuthRequest(self, msgFromClient):
        self.sendDataAuth(self.gs, msgFromClient)
        response = io.readMessage(self.gs)
        counter = 1
        while response != '<ACK>' and counter<4:
            counter += 1
            self.sendDataAuth(self.gs, msgFromClient)
            response = io.readMessage(self.gs)
        if response != '<ACK>':
            raise Exception('The addressee cannot receive data correctly.  ')
        msgFromProc = io.readMessage(self.gs) #the answer
        if not sm.isLRC_ok(msgFromProc):
            print('\nThe LRC check returned false for four times.  \n')
            io.writeMessage('<NACK>')
            io.closeConnection(self.gs)
        else:
            io.writeMessage(self.gs, '<ACK>')
            io.writeMessage(self.gs, '<EOT>')
            io.closeConnection(self.gs)


    def handleGatewayRequest(self, msgFromClient):
        try:
            self.gs = io.establishConnection(('localhost', 12000)) #throws exception
            print('\nConnected to the gateway.\n')
            if self.getPath(msgFromClient) == '/gatewaySD/auth':
                self.manageAuthRequest(msgFromClient)
            else:
                pass
        except socket.error as exc:
            print('Connection to gateway failed.\n')
            s = io.setCode('HTTP/1.1', 500)
            s = io.setMessageAnswer(s, 'Internal Server Error')
            s = io.setConnection(s, 'Close\n\n')
            s = s + 'Socket error: Connection to the gateway failed. \n'
            io.writeMessage(self.csocket, s)
            print(f'Sent \n{s} to the client after POST request\n')
            io.closeConnection(self.csocket)
