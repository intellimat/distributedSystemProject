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
        elif not self.isPathCorrect(msgFromClient):
            self.sendNotExistingPath()
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

    def isPathCorrect(self, msgFromClient):
        path = self.getPath(msgFromClient)
        if path == '' or path == '/' or path == '/index.html' or path == '/gatewaySD' or path[0:11] == '/gatewaySD/':
            return True
        return False


    def sendNotExistingPath(self):
        html_page = io.readFile(os.path.curdir + '/error.html')
        newContent = '''<body>\n<div id="msg_instruction"> 404 Not Found </div>
                        <div id="details"> The path specified in the HTTP request is does not exist.
                                             </div>'''
        v = html_page.split('<body>')
        updatedHTML = v[0] + newContent + v[1]
        page_length = len(updatedHTML)
        s = io.setCode('HTTP/1.1', 404)
        s = io.setMessageAnswer(s, 'Not Found')
        s = io.setContentLength(s, page_length)
        s = io.setContentType(s, 'text/html')
        s = io.setConnection(s, 'Close\n\n')
        s = s + updatedHTML
        io.writeMessage(self.csocket, s)

    def checkMethod(self, clientMsg):
        if len(clientMsg) > 0:
            httpMethod = clientMsg.split()[0]
            if httpMethod == 'GET' or httpMethod == 'POST':
                return True
            return False

    def sendMethodNotAllowed(self):
        html_page = io.readFile(os.path.curdir + '/error.html')
        newContent = '''<body>\n<div id="msg_instruction"> 405 Method Not Allowed </div>
                        <div id="details"> The method specified in the HTTP requested is not allowed.
                                            the only two methods supported are GET and POST. </div>'''
        v = html_page.split('<body>')
        updatedHTML = v[0] + newContent + v[1]
        page_length = len(updatedHTML)

        s = io.setCode('HTTP/1.1', 405)
        s = io.setMessageAnswer(s, 'Method Not Allowed')
        s = io.setContentLength(s, page_length)
        s = io.setContentType(s, 'text/html')
        s = io.setConnection(s, 'Close\n\n')
        s = s + updatedHTML
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
        if len(clientMsg) > 0:
            path = clientMsg.split()[1]
            print(f"The path is: {path}\n")
            return path
        else:
            return ''

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
        msgFromGateway = io.readMessage(self.gs) #the answer
        if not sm.isLRC_ok(msgFromGateway):
            print('\nThe LRC check returned false for four times.  \n')
            io.writeMessage('<NACK>')
            io.closeConnection(self.gs)
        else:
            io.writeMessage(self.gs, '<ACK>')
            io.writeMessage(self.gs, '<EOT>')
            io.closeConnection(self.gs)
            self.sendHTMLresponseToClient(msgFromGateway)

    def sendHTMLresponseToClient(self, msgFromGateway):
        html_page = msgFromGateway.split('<STX>')[1].split('<ETX>')[0]
        pageLength = len(html_page)
        s = io.setCode('HTTP/1.1', 200)
        s = io.setMessageAnswer(s, 'OK')
        s = io.setContentLength(s, pageLength)
        s = io.setContentType(s, 'text/html')
        s = io.setConnection(s, 'Close')
        s = s + f'\n\n{html_page}'
        print(f"Message to send to the client (user in this case) as response: \n\n HTML page")
        io.writeMessage(self.csocket, s)


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
            print(f'Exception: {exc}')
            ''''''
            html_page = io.readFile(os.path.curdir + '/error.html')
            newContent = '''<body>\n<div id="msg_instruction"> 500 Internal Server Error </div>
                            <div id="details"> The gateway serve cannot be reached.
                                                Try again later. </div>'''
            v = html_page.split('<body>')
            updatedHTML = v[0] + newContent + v[1]
            page_length = len(updatedHTML)

            s = io.setCode('HTTP/1.1', 500)
            s = io.setMessageAnswer(s, 'Internal Server Error')
            s = io.setContentLength(s, page_length)
            s = io.setContentType(s, 'text/html')
            s = io.setConnection(s, 'Close\n\n')
            s = s + updatedHTML
            io.writeMessage(self.csocket, s)
            io.closeConnection(self.csocket)
