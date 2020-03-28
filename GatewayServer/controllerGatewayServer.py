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
        self.manageClientInteraction()
        '''
        if not self.isCorrectPath(path):
            pass

        elif resourcePath == '/info':
            self.handleInformationRequest()

        elif resourcePath == '/auth':
            self.managePayment(msgFromClient)

        elif resourcePath == '/status':
            pass

        elif resourcePath == '/fl':
            pass

        elif resourcePath == '/ul':
            pass
        else:
            pass
            '''
    def manageAuthRequest(self):
        #here we gotta put the logic
        outcome = 'ok'
        if outcome == 'ok':
            html_page = io.readFile(os.path.curdir + '/authResponse.html')
            v = html_page.split('<div id="outcome">')
            html_page = v[0] + '<div id="outcome"> Operation accepted. ' + v[1]
            lrc_answer = sm.getLRCvalueFromString(html_page)
            io.writeMessage(self.csocket, f'<STX>{html_page}<ETX>{lrc_answer}')
        else:
            html_page = io.readFile(curdir + '/authResponse.html')
            v = html_page.split('<div id="outcome">')
            html_page = v[0] + '<div id="outcome"> Operation refused. ' + v[1]
            lrc_answer = sm.getLRCvalueFromString(html_page)
            io.writeMessage(self.csocket, f'<STX>{html_page}<ETX>{lrc_answer}')
        msgFromClient = io.readMessage(self.csocket)
        counter = 1
        while msgFromClient!='<ACK>' and counter<4:
            counter+=1
            io.writeMessage(self.csocket, f'<STX>{html_page}<ETX>{str(lrc_answer)}')
            msgFromClient = io.readMessage(self.csocket)
        msgFromClient = io.readMessage(self.csocket) #expecting the <EOT> from the client

    def readOperationCode(self,msgFromClient):
        v = msgFromClient.split('<STX>')
        return int(v[1][0])

    def manageClientInteraction(self):
        msgFromClient = io.readMessage(self.csocket)
        if msgFromClient == '<ENQ>':
            io.writeMessage(self.csocket, '<ACK>')
            msgFromClient = io.readMessage(self.csocket)
            counter=1
            lrc_correct = sm.isLRC_ok(msgFromClient)
            while (not lrc_correct) and counter<4:
                counter+=1
                io.writeMessage(self.csocket, '<NACK>')
                msgFromClient = io.readMessage(self.csocket)
                lrc_correct = sm.isLRC_ok(msgFromClient)
            if lrc_correct:
                io.writeMessage(self.csocket, '<ACK>')
                op_code = self.readOperationCode(msgFromClient)
                if(op_code == 1):
                    self.manageAuthRequest()
                else:
                    pass


        else:
            print('\nRAMO ELSE\n')
            io.writeMessage(self.csocket,'<NACK>')
            io.writeMessage(self.csockeet, '<EOT>')

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

    def getProcessor(self, msgFromClient):
        basicPath = pathlib.Path.cwd()
        filePath = pathlib.Path(basicPath, 'processorsMappingAndAddresses', 'Bines.txt')
        f = io.readFile(filePath)
        body = msgFromClient.split('\r\n\r\n')[1]
        data = sm.getJSONobjectFromString(body)
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
        p_socket = io.establishConnection(address) #raise exception


        io.closeConnection(p_socket)
        self.sendResponseToWebServer(param)

    def sendResponseToWebServer(self,parm):
        pass

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
        data = sm.getJSONobjectFromString(body)
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
