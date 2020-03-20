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
        proc = self.getProcessor(msgFromClient)
        print(f'The processor is: {proc}')
        ''' here goes all the logic of the gateway server '''
        path = self.getPOSTpath()

        if not self.isCorrectPath(path):
            pass
        elif not self.isCorrectData(msgFromClient):
            pass
        else:
            self.managePayment(msgFromClient)


    def sendMethodNotAllowed(self):
        response_msg = 'HTTP/1.1 405 Method Not Allowed\n'
        io.writeResponse(response_msg)

    def sendBadRequest(self):
        response_msg = 'HTTP/1.1 400 Bad Request\n'
        io.writeResponse(response_msg)

    def isPOSTRequest(self,clientMsg):
        return clientMsg[0:4] == 'POST'

    def getPOSTpath(self,clientMsg):
        path = clientMsg.split()[1]
        print(f"the path is {path}")
        return path

    def getJSONobjectFromString(self, s):
        return json.loads(s)

    def getProcessor(self, msgFromClient):
        basicPath = pathlib.Path.cwd()
        filePath = pathlib.Path(basicPath, 'processorsMappingAndAddresses', 'Bines.txt')
        print(f'File path is:\n {filePath}')
        f = io.readFile(filePath)
        data = self.getJSONobjectFromString(msgFromClient)
        CardNumber = data.get('cardNumber')
        firstDigit = cardNumber[0]

        buffer = []
        prec = ''
        for c in f:
            if c != '\n':
                buffer.append(c)
                if (prec == '#' and buffer[0] == firstDigit):
                    return buffer[3]
                elif prec == '#':
                    buffer = []
                    prec = ''
                else:
                    prec = c


    def managePayment(self, msgFromClient):
        processorNumber = self.getProcessor()
        address = self.findAddress(processorNumber)
        self.callProcessor(address)
        'wait for response and then forward the response to the client'

    def callProcessor(self, address):
        pass

    def findAddress(self, processor):
        pass

    def isCorrectPath(self, path):
        return path == '/pay'

    def isCorrectData(self, msgFromClient):
        data = self.getJSONobjectFromString(msgFromClient)
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
