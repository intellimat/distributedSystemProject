import socket
import os, sys
import json
import pathlib

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

        ''' here goes all the logic of the gateway server '''
        path = self.getPath(msgFromClient)
        print(f'\n\nPath of the request is {path}\n\n')

        if not self.isCorrectPath(path):
            print('\n\nEnter isCorrectPath method\n\n')

        elif path == '/gatewaySD/info':
            self.handleInformationRequest()

        elif path == '/gatewaySD':
            self.managePayment(msgFromClient)
        else:
            pass

    def getProcessorsInfo(self):
        basicPath = pathlib.Path.cwd().parent

        filePath = pathlib.Path(basicPath, 'Procesador1', 'config.txt')
        f1 = io.readFile(filePath)

        filePath = pathlib.Path(basicPath, 'Procesador2', 'config.txt')
        f2 = io.readFile(filePath)

        filePath = pathlib.Path(basicPath, 'Procesador3', 'config.txt')
        f3 = io.readFile(filePath)
        style = 'style = "margin-left: 2em; font-weight: normal; font-size: 22px;"'
        allProcsConfig = f'<ul>\n<li {style} >{f1}</li><br>\n<li {style} >{f2}</li><br>\n<li {style} >{f3}</li><br>\n</ul>'

        return allProcsConfig

    def handleInformationRequest(self):
        data = self.getProcessorsInfo()
        page = io.readFile(os.curdir + '/info.html')
        v = page.split('<div class="infoProcs">')
        updatedHTML = v[0] + data + v[1]
        pageLength = len(updatedHTML)
        # s is the response message
        s = io.setCode('HTTP/1.1', 200)
        s = io.setResponseAnswer(s, 'OK')
        s = io.setContentLength(s, pageLength)
        s = io.setContentType(s, 'text/html')
        s = io.setConnection(s, 'Close')
        s = s + f'\n\n{updatedHTML}'
        print(f"Message to send to the client (WebServer in this case) as response: \n\n HTML page")
        io.writeResponse(self.csocket, s)
        io.closeConnection(self.csocket)

    def sendProcessorsInfoPage(self):
        page = io.readFile(os.curdir + '/info.html')


    def sendMethodNotAllowed(self):
        response_msg = 'HTTP/1.1 405 Method Not Allowed\n'
        io.writeResponse(self.csocket, response_msg)

    def sendBadRequest(self):
        response_msg = 'HTTP/1.1 400 Bad Request\n'
        io.writeResponse(self.csocket, response_msg)

    def isPOSTRequest(self,clientMsg):
        return clientMsg[0:4] == 'POST'

    def getPath(self,clientMsg):
        path = clientMsg.split()[1]
        return path

    def getJSONobjectFromString(self, s):
        return json.loads(s)

    def getProcessor(self, msgFromClient):
        basicPath = pathlib.Path.cwd()
        filePath = pathlib.Path(basicPath, 'processorsMappingAndAddresses', 'Bines.txt')
        f = io.readFile(filePath)
        body = msgFromClient.split('\r\n\r\n')[1]
        data = self.getJSONobjectFromString(body)
        cardNumber = data.get("cardNumber")
        firstDigit = cardNumber[0]

        buffer = []
        prec = ''
        for c in f:
            if c != '\n':
                buffer.append(c)
                if (prec == '#' and buffer[0] == firstDigit):
                    return buffer[2]
                elif prec == '#':
                    buffer = []
                    prec = ''
                else:
                    prec = c


    def managePayment(self, msgFromClient):
        ''' here we gotta call checkData '''
        processorNumber = self.getProcessor()
        address = self.findAddress(processorNumber)
        self.callProcessor(address)
        'wait for response and then forward the response to the client'

    def callProcessor(self, address):
        pass

    def findAddress(self, processor):
        pass

    def isCorrectPath(self, path):
        if path == '/gatewaySD' or path == '/gatewaySD/info':
            return True
        return False

    def isCorrectData(self, msgFromClient):
        body = msgFromClient.split('\r\n\r\n')[1]
        data = self.getJSONobjectFromString(body)
        for field in data:  #check no empty fields
            if len(field) < 1:
                return False

        if data.get("cardNumber") != 16:
            return False

        if data.get("cvv") != 3:
            return False

        if data.get("amount") <= 0:
            return False

        return True
