import socket
import os, sys
import json
import pathlib

pathRepo = os.path.dirname(os.path.dirname(os.getcwd()))
sys.path.insert(1, pathRepo)

from distributedSystemProject.utils import inputOutput as io
from distributedSystemProject.utils import stringManager as sm
from distributedSystemProject.utils.Exception import NetworkException, ProcessorAddressNotFound

class Controller(object):
    def __init__(self,csocket):
        self.csocket = csocket
        self.host, self.port = self.csocket.getpeername()

    def parseRequest(self):
        try:
            self.acceptConnection()
            self.receiveMessageAndRespond(self.csocket)
        except NetworkException as exc:
            print(f'\n{exc}\n')
            print(exc.message)


    def formatAuthRequestToProcessor(self, wsMsgContent):
        amount = wsMsgContent.split('Parameters[]:')[1].split('\n')[0].split('#')[-1]
        s = sm.setResourcePath('/auth')
        params = f'{amount}'
        s = sm.setParameters(s, params)
        s = sm.setHeaders(s,'')
        return s

    def getAuthOutcome(self, wsMsgContent):
        processorNumber = self.selectProcessor(wsMsgContent)
        try:
            address = self.findAddress(processorNumber)
            p_socket = io.establishConnection(address)
            s = self.formatAuthRequestToProcessor(wsMsgContent)
            responseFromProcessor = self.sendMessageAndGetResponse(p_socket, s).split('<STX>')[1].split('<ETX>')[0]
            return responseFromProcessor
        except ProcessorAddressNotFound as exc:
            print(f'\n{exc}\n')
            return exc.message
        except NetworkException as exc:
            print(f'\n{exc}\n')
            return exc.message

    def getProcessorsInfo(self):
        processorsAddresses = []

        try:
            p1_address = self.findAddress(1)
            processorsAddresses.append(p1_address)
        except ProcessorAddressNotFound as exc:
            print(f'\n{exc}\n')
        finally:
            try:
                p2_address = self.findAddress(2)
                processorsAddresses.append(p2_address)
            except ProcessorAddressNotFound as exc:
                print(f'\n{exc}\n')
            finally:
                try:
                    p3_address = self.findAddress(3)
                    processorsAddresses.append(p3_address)

                except ProcessorAddressNotFound as exc:
                    print(f'\n{exc}\n')
                finally:
                    try:
                        for p_address in processorsAddresses:
                            p_socket = io.establishConnection(p_address[0], p_address[1])

                        style = 'style = "margin-left: 2em; font-weight: normal; font-size: 22px;"'
                        allProcsConfig = f'<ul>\n<li {style} >{f1}</li><br>\n<li {style} >{f2}</li><br>\n<li {style} >{f3}</li><br>\n</ul>'

                        return allProcsConfig

                    except NetworkException as exc:
                        print(f'\n{exc}\n')



            #raise socket exception
    def handleInformationRequest(self):
        #try except socket exception
        data = self.getProcessorsInfo()
        page = io.readFile(os.curdir + '/info.html')
        v = page.split('<div class="infoProcs">')
        updatedHTML = v[0] + data + v[1]
        pageLength = len(updatedHTML)
        # s is the response message
        s = sm.setCode('HTTP/1.1', 200)
        s = sm.setMessageAnswer(s, 'OK')
        s = sm.setContentLength(s, pageLength)
        s = sm.setContentType(s, 'text/html')
        s = sm.setConnection(s, 'Close')
        s = s + f'\n\n{updatedHTML}'
        print(f"Message to send to the client (WebServer in this case) as response: \n\n HTML page")
        io.writeMessage(self.csocket, s)
        io.closeConnection(self.csocket)


    def getPath(self,clientMsg):
        path = clientMsg.split()[1]
        return path

    def selectProcessor(self, clMsgContent):
        basicPath = pathlib.Path.cwd()
        filePath = pathlib.Path(basicPath, 'processorsMappingAndAddresses', 'Bines.txt')
        f = io.readFile(filePath)
        firstDigit = clMsgContent.split('Parameters[]:')[1].split('\n')[0].split('#')[1][0]
        print(f'Card_firstDigit: {firstDigit}')

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

    def findAddress(self, processor):
        print(f'Getting address of processor: {processor}')
        basicPath = pathlib.Path.cwd()
        filePath = pathlib.Path(basicPath, 'processorsMappingAndAddresses', 'Procesadores.txt')
        f = io.readFile(filePath)
        buffer = []
        for c in f:
            #print(f'Current buffer is: {buffer}\n')
            if c != '\n':
                buffer.append(c)
            elif buffer[0] == processor:
                s = ''.join(buffer)
                print(f'\nAddress: {s}\n')
                v = s.split('#')
                IP = v[1]
                PORT = int(v[2])
                return (IP,PORT)
            else:
                buffer = []

        raise ProcessorAddressNotFound(f'The address of the processor number "{processor}" cannot be found. ')

    def isCorrectPath(self, path):
        if path == '/gatewaySD/auth' or path == '/gatewaySD/info':
            return True
        return False

    def isCorrectData(self, msgFromClient):
        if data.get("cardNumber") != 16:
            return False

        if data.get("cvv") != 3:
            return False

        if data.get("amount") <= 0:
            return False

        return True

    def acceptConnection(self):
        msgFromWs = io.readMessage(self.csocket)
        while msgFromWs != '<ENQ>' and msgFromWs != '<EOT>':
            msgFromWs = io.readMessage(self.csocket)
        if msgFromWs == '<ENQ>':
            io.writeMessage(self.csocket, '<ACK>')
        else:
            raise NetworkException('Impossible to establish a connection. ')

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
            raise NetworkException('The processor cannot receive data correctly.  ')
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
                raise NetworkException("The gateway couldn't receive the response correctly from the processor. ")

    def receiveMessageAndRespond(self, p_socket):
        message = io.readMessage(p_socket)
        if message != '<EOT>':
            content = message.split('<STX>')[1].split('<ETX>')[0]
            lrcReceived = message.split('<ETX>')[1]
            lrcCalculated = str(sm.getLRCvalueFromString(content))
            receivedEOT = False
            print(f'lrcCalculated = {lrcCalculated}\nlrcReceived = {lrcReceived}')
            while (not receivedEOT) and (lrcCalculated != lrcReceived):
                io.writeMessage(p_socket, '<NACK>')
                message = io.readMessage(p_socket)
                if message == '<EOT>':
                    receivedEOT = True
                else:
                    content = message.split('<STX>')[1].split('<ETX>')[0]
                    lrcReceived = message.split('<ETX>')[1]
                    lrcCalculated = str(sm.getLRCvalueFromString(content))
            if not receivedEOT:
                io.writeMessage(p_socket,'<ACK>')
                html_page = self.handleMessageAndGetHTML(content)
                lrcHTML = sm.getLRCvalueFromString(html_page)
                msgToSend = f'<STX>{html_page}<ETX>{lrcHTML}'
                io.writeMessage(p_socket,msgToSend)
                response = io.readMessage(p_socket)
                counter = 0
                while response != '<ACK>' and counter<4:
                    counter += 1
                    io.writeMessage(p_socket, msgToSend)
                    response = io.readMessage(p_socket)
                if response != '<ACK>':
                    io.writeMessage(p_socket, '<EOT>')
                    raise NetworkException('The web server cannot receive data correctly.  ')
                else:
                    endMessage = io.readMessage(p_socket) #waiting for <EOT>
            else:
                raise NetworkException("The gateway couldn't received the data correctly from the web server. ")

    def handleMessageAndGetHTML(self, msgContent):
        resourcePath = msgContent.split('ResourcePath:')[1].split('\n')[0]

        if resourcePath == '/auth':
            outcome = self.getAuthOutcome(msgContent)
            html = self.getUpdatedAuthHTML(outcome)
        elif resourcePath == '/index':
            outcome = self.getProcessorsInfo(msgContent)
            html = self.getUpdatedProcessorInfoHTML(outcome)
        else:
            pass
        return html

    def getUpdatedAuthHTML(self, outcome):
        html_page = io.readFile(os.path.curdir + '/authResponse.html')
        v = html_page.split('<div id="outcome">')
        html_page = v[0] + '<div id="outcome">' + outcome + v[1]
        return html_page

    def getUpdatedProcessorInfoHTML(self,outcome):
        pass
