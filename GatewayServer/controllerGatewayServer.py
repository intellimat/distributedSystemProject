import socket
import os, sys
import json
import pathlib

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
        print(f"\nServer received the message:\n\n\n '{msgFromClient}' \n\n\nfrom {self.host} on port {self.port}\n\n\n")

        path = self.getPath(msgFromClient)
        print(f'\n\nPath of the request is {path}\n\n')

        if not self.isCorrectPath(path):
            pass

        elif path == '/gatewaySD/info':
            self.handleInformationRequest()

        elif path == '/gatewaySD/auth':
            self.managePayment(msgFromClient)

        elif path == '/gatewaySD/status':
            pass

        elif path == '/gatewaySD/fl':
            pass

        elif path == '/gatewaySD/ul':
            pass
        else:
            pass

    def connectToProcessor(self, IP, PORT):
        # AF_INET means IPv4, SCOCK_STREM means TCP
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((IP, PORT))
        return s

    def getProcessorsInfo(self):
        try:
            p1_address = self.findAddress(1)
            p2_address = self.findAddress(2)
            p3_address = self.findAddress(3)
        except Exception as exc:
            print(f'\n{exc}\n\n')

        try:
            p1_socket = self.connectToProcessor(p1_address[0], p1_address[1])
            p2_socket = self.connectToProcessor(p2_address[0], p2_address[1])
            p3_socket = self.connectToProcessor(p3_address[0], p3_address[1])

            httpRequest = 'GET /info HTTP/1.1\n\n'

            io.writeMessage(p1_socket, httpRequest)
            io.writeMessage(p2_socket, httpRequest)
            io.writeMessage(p3_socket, httpRequest)

            f1 = io.readMessage(p1_socket)
            f2 = io.readMessage(p2_socket)
            f3 = io.readMessage(p3_socket)

            style = 'style = "margin-left: 2em; font-weight: normal; font-size: 22px;"'
            allProcsConfig = f'<ul>\n<li {style} >{f1}</li><br>\n<li {style} >{f2}</li><br>\n<li {style} >{f3}</li><br>\n</ul>'

            return allProcsConfig

        except socket.error as exc:
            print('Connection to a processor failed. ')
            '''
            s = io.setCode('HTTP/1.1', 500)
            s = io.setMessageAnswer(s, 'Internal Server Error')
            s = io.setConnection(s, 'Close\n\n')
            s = s + 'Socket error: Connection to a processor failed. \n'
            io.writeMessage(self.csocket, s)
            print(f'Sent \n{s} to the client (WebServer in this case) after request\n')
            io.closeConnection(self.csocket)
            '''
            #raise socket exception

    def handleInformationRequest(self):
        #try except socket exception
        data = self.getProcessorsInfo()
        page = io.readFile(os.curdir + '/info.html')
        v = page.split('<div class="infoProcs">')
        updatedHTML = v[0] + data + v[1]
        pageLength = len(updatedHTML)
        # s is the response message
        s = io.setCode('HTTP/1.1', 200)
        s = io.setMessageAnswer(s, 'OK')
        s = io.setContentLength(s, pageLength)
        s = io.setContentType(s, 'text/html')
        s = io.setConnection(s, 'Close')
        s = s + f'\n\n{updatedHTML}'
        print(f"Message to send to the client (WebServer in this case) as response: \n\n HTML page")
        io.writeMessage(self.csocket, s)
        io.closeConnection(self.csocket)

    def sendMethodNotAllowed(self):
        response_msg = 'HTTP/1.1 405 Method Not Allowed\n'
        io.writeMessage(self.csocket, response_msg)

    def sendBadRequest(self):
        response_msg = 'HTTP/1.1 400 Bad Request\n'
        io.writeMessage(self.csocket, response_msg)

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
        processorNumber = self.getProcessor(msgFromClient)
        address = self.findAddress(processorNumber)
        p_socket = self.establishConnection(address)
        self.sendDataToProcessor(p_socket, msgFromClient)
        response = io.readMessage(p_socket)
        counter = 1
        while response != '<ACK>' and counter<3:
            counter += 1
            self.sendDataToProcessor(p_socket, msgFromClient)
            response = io.readMessage(p_socket)
        if response != '<ACK>':
            raise Exception('The processor cannot receive data correctly.  ')
        msgFromProc = io.readMessage(p_socket) #the answer
        if not self.isLRC_ok(msgFromProc):
            pass
        else:
            io.writeMessage(p_socket, '<ACK>')
            io.writeMessage(p_socket, '<EOT>')
            io.closeConnection(p_socket)
            self.sendResponseToWebServer(param)

    def isLRC_ok(self, msgFromProc):
        v = msgFromProc.split('<STX>')
        vu = v[1].split('<ETX>')
        answer = vu[0]
        lrc_fromProc = int(vu[1])
        calculated_lrc = sm.getLRCvalueFromString(answer)
        return calculated_lrc == lrc_fromProc

    def sendResponseToWebServer(self,parm):
        pass


    def establishConnection(self,address):
        p_IP = address[0]
        p_PORT = address[1]
        p_socket = self.connectToProcessor(p_IP, p_PORT)
        io.writeMessage(p_socket,'<ENQ>')
        response = io.readMessage(p_socket)
        counter = 1
        while response != '<ACK>' and counter<3:
            counter += 1
            io.writeMessage(p_socket,'<ENQ>')
            response = io.readMessage(p_socket)
        if response != '<ACK>':
            raise Exception('Impossible to establish connection with the selected processor. ')
        print('Connection to processor established. ')
        return p_socket

    def sendDataToProcessor(self, msgFromClient):
        body = msgFromClient.split('\r\n\r\n')[1]
        data = self.getJSONobjectFromString(body)
        name = data.get('name'),
        surname = data.get('surname'),
        cardNumber = data.get('cardNumber')
        cvv = data.get('cvv')
        expDate = data.get('expDate')
        amount = data.get('amount')
        s = f'1#{name} {surname}#{cardNumber}#{amount}#{cvv}#{expDate}'
        lrc = sm.getLRCvalueFromString(s)
        s = '<STX>' + s + '<ETX>' + lrc
        io.writeMessage(p_socket, s)

    def fromatAuthMessage(self):
        pass

    def findAddress(self, processor):
        basicPath = pathlib.Path.cwd()
        filePath = pathlib.Path(basicPath, 'processorsMappingAndAddresses', 'Procesadores.txt')
        f = io.readFile(filePath)
        print(f'\nFILE LOADED IS:\n{f}')
        buffer = []
        for c in f:
            print(f'Current buffer is: {buffer}\n')
            if c != '\n':
                buffer.append(c)
            elif int(buffer[0]) == processor:
                s = ''.join(buffer)
                print(f'\nAddress: {s}\n')
                v = s.split('#')
                IP = v[1]
                PORT = int(v[2])
                return (IP,PORT)
            else:
                buffer = []

        raise Exception('Processor not present in the list')

    def isCorrectPath(self, path):
        if path == '/gatewaySD/auth' or path == '/gatewaySD/info':
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
