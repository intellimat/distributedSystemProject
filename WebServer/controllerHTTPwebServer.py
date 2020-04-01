import os
import sys
import socket
import json

pathRepo = os.path.dirname(os.path.dirname(os.getcwd()))
sys.path.insert(1, pathRepo)

from distributedSystemProject.utils import inputOutput as io
from distributedSystemProject.utils import stringManager as sm
from distributedSystemProject.utils.Exception import NetworkException

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
        accessiblePaths = { '0': '/favicon.ico',
                            '1': '',
                            '2': '/',
                            '3': '/index.html',
                            '4': '/gatewaySD/index',
                            '5': '/gatewaySD/auth',
                            '6': '/gatewaySD/status',
                            '7': '/gatewaySD/fl',
                            '8': '/gatewaySD/ul'}

        path = self.getPath(msgFromClient).split('?')[0]
        for n in accessiblePaths:
            if accessiblePaths.get(n) == path:
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
        s = sm.setCode('HTTP/1.1', 404)
        s = sm.setMessageAnswer(s, 'Not Found')
        s = sm.setContentLength(s, page_length)
        s = sm.setContentType(s, 'text/html')
        s = sm.setConnection(s, 'Close\n\n')
        s = s + updatedHTML
        io.writeMessage(self.csocket, s)

    def checkMethod(self, clientMsg):
        if len(clientMsg) > 0:
            httpMethod = clientMsg.split()[0]
            if httpMethod == 'GET':
                return True
            return False

    def sendMethodNotAllowed(self):
        html_page = io.readFile(os.path.curdir + '/error.html')
        newContent = '''<body>\n<div id="msg_instruction"> 405 Method Not Allowed </div>
                        <div id="details"> The method specified in the HTTP requested is not allowed.
                                            the only method supported is GET </div>'''
        v = html_page.split('<body>')
        updatedHTML = v[0] + newContent + v[1]
        page_length = len(updatedHTML)

        s = sm.setCode('HTTP/1.1', 405)
        s = sm.setMessageAnswer(s, 'Method Not Allowed')
        s = sm.setContentLength(s, page_length)
        s = sm.setContentType(s, 'text/html')
        s = sm.setConnection(s, 'Close\n\n')
        s = s + updatedHTML
        io.writeMessage(self.csocket, s)

    def sendBadRequest(self):
        html_page = io.readFile(os.path.curdir + '/error.html')
        newContent = '''<body>\n<div id="msg_instruction"> 400 Bad Request </div>
                        <div id="details"> The server cannot process your request.
                                             If it's an auth request, check that all the parameters:<br>
                                             name, cardNumber, cvv, expDate and amount are present in the url.
                                             </div>'''
        v = html_page.split('<body>')
        updatedHTML = v[0] + newContent + v[1]
        page_length = len(updatedHTML)

        s = sm.setCode('HTTP/1.1', 400)
        s = sm.setMessageAnswer(s, 'Bad Request')
        s = sm.setContentLength(s, page_length)
        s = sm.setContentType(s, 'text/html')
        s = sm.setConnection(s, 'Close\n\n')
        s = s + updatedHTML
        io.writeMessage(self.csocket, s)
        io.closeConnection(self.csocket)

    def isHomepageRequest(self, clientMsg):
        httpMethod = clientMsg.split()[0]
        path = self.getPath(clientMsg)
        return (httpMethod == 'GET') and (path == '/' or path == '/index.html')

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
        s = sm.setCode('HTTP/1.1', 200)
        s = sm.setMessageAnswer(s, 'OK')
        s = sm.setContentLength(s, pageLength)
        s = sm.setContentType(s, 'text/html')
        s = sm.setConnection(s, 'Close')
        s = s + f'\n\n{page}'
        io.writeMessage(self.csocket, s)

    def sendFavicon(self):
        favicon = io.readFile(os.curdir + '/favicon.ico')
        faviconLength = len(favicon)
        # s is the response message
        s = sm.setCode('HTTP/1.1', 200)
        s = sm.setMessageAnswer(s, 'OK')
        s = sm.setContentLength(s, faviconLength)
        s = sm.setContentType(s, 'image/x-icon')
        s = sm.setConnection(s, 'Close')
        s = s + f'\n\n{favicon}'
        print(f"Message to send to the client as response: favicon ")
        io.writeMessage(self.csocket, s)

    def isDataAuthCorrect(self, msgFromClient):
        path = self.getPath(msgFromClient)
        p = sm.getQueryStringParameters(path)
        allParameters = 'name' in p and 'cardNumber' in p and 'cvv' in p and 'expDate' in p and 'amount' in p
        if not allParameters:
            return False
        return True

    def formatAuthRequest(self, msgFromClient):
        path = self.getPath(msgFromClient)
        parameters = sm.getQueryStringParameters(path)
        name = parameters.get('name')
        cardNumber = parameters.get('cardNumber')
        cvv = parameters.get('cvv')
        expDate = parameters.get('expDate')
        amount = parameters.get('amount')
        s = sm.setResourcePath('/auth')
        params = f'{name}#{cardNumber}#{cvv}#{expDate}#{amount}'
        s = sm.setParameters(s, params)
        s = sm.setHeaders(s,'')
        return s

    def manageAuthRequest(self, msgFromClient):
        if self.isDataAuthCorrect(msgFromClient):
            s = self.formatAuthRequest(msgFromClient)
            responseFromGateway = self.sendMessageAndGetResponse(self.gs, s)
            self.sendHTMLresponseToClient(responseFromGateway)

        else:
            self.sendBadRequest()
            io.writeMessage(self.gs, '<EOT>')
            io.closeConnection(self.gs)

    def sendHTMLresponseToClient(self, msgFromGateway):
        html_page = msgFromGateway.split('<STX>')[1].split('<ETX>')[0]
        pageLength = len(html_page)
        s = sm.setCode('HTTP/1.1', 200)
        s = sm.setMessageAnswer(s, 'OK')
        s = sm.setContentLength(s, pageLength)
        s = sm.setContentType(s, 'text/html')
        s = sm.setConnection(s, 'Close')
        s = s + f'\n\n{html_page}'
        print(f"Message to send to the client (user in this case) as response: \n\n HTML page")
        io.writeMessage(self.csocket, s)


    def handleGatewayRequest(self, msgFromClient):
        try:
            self.gs = io.establishConnection(('localhost', 12000)) #throws exception
            print('\nConnected to the gateway.\n')
            path = self.getPath(msgFromClient).split('?')[0]

            if path == '/gatewaySD/auth':
                self.manageAuthRequest(msgFromClient)
            elif path == '/gatewaySD/index':
                self.manageIndexReuqest(msgFromClient)
                pass
            elif path[:17] == '/gatewaySD/status':
                pass
            elif path[:13] == '/gatewaySD/fl':
                pass
            elif path[:13] == '/gatewaySD/ul':
                pass
            else:
                pass
        except NetworkException as exc:
            print('Connection to the gateway failed.\n')
            print(f'\n{exc}\n')
            self.sendInternalServerError(exc.message)


    def sendInternalServerError(self, exc):
        html_page = io.readFile(os.path.curdir + '/error.html')
        newContent = '''<body>\n<div id="msg_instruction"> 500 Internal Server Error </div>
                        <div id="details"> The gateway server cannot be reached properly.
                                            Try again later.<br></div>'''
        newContent = newContent + f'<div>Error detected: {exc}</div>'
        v = html_page.split('<body>')
        updatedHTML = v[0] + newContent + v[1]
        page_length = len(updatedHTML)

        s = sm.setCode('HTTP/1.1', 500)
        s = sm.setMessageAnswer(s, 'Internal Server Error')
        s = sm.setContentLength(s, page_length)
        s = sm.setContentType(s, 'text/html')
        s = sm.setConnection(s, 'Close\n\n')
        s = s + updatedHTML
        io.writeMessage(self.csocket, s)
        io.closeConnection(self.csocket)

    def sendMessageAndGetResponse(self, p_socket, message): #returns the response
        lrc = sm.getLRCvalueFromString(message)
        s = '<STX>' + message + '<ETX>' + str(lrc)
        io.writeMessage(p_socket, s)
        response = io.readMessage(p_socket)
        counter = 0
        while response != '<ACK>' and counter<4:
            counter += 1
            io.writeMessage(p_socket, s)
            response = io.readMessage(p_socket)
        if response != '<ACK>':
            io.writeMessage(p_socket, '<EOT>')
            raise socket.error('The gateway server cannot receive data correctly.  ')
        else: #<ACK> for the data sent
            response = io.readMessage(p_socket) #the answer
            receivedEOT = False
            while not receivedEOT and not sm.isLRC_ok(response):
                io.writeMessage(p_socket, '<NACK>')
                response = io.readMessage(p_socket)
                if response == '<EOT>':
                    receivedEOT = True
            if receivedEOT == False: #means that I received correctly the response
                io.writeMessage(p_socket,'<ACK>')
                io.writeMessage(p_socket,'<EOT>')
                return response
            else:
                raise socket.error("The web server couldn't receive the response correctly from the gateway server. ")
