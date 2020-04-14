import socket
import os, sys
import pathlib

pathRepo = os.path.dirname(os.path.dirname(os.getcwd()))
sys.path.insert(1, pathRepo)

from distributedSystemProject.utils import inputOutput as io
from distributedSystemProject.utils import stringManager as sm
from distributedSystemProject.utils.Exception import NetworkException, ProcessorAddressNotFound, ParametersNotCorrect

class Controller(object):
    def __init__(self,csocket):
        self.csocket = csocket
        self.host, self.port = self.csocket.getpeername()
        self.numberOfProcessors = 3

    def parseRequest(self):
        try:
            self.acceptConnection()
            self.receiveMessageAndRespond(self.csocket)
        except NetworkException as exc:
            print(f'\n{exc}\n')
            print(exc.message)

    def formatParameterRequest(self, wsMsgContent):
        resourcePath = wsMsgContent.split('ResourcePath:')[1].split('\n')[0]
        s = sm.setResourcePath(resourcePath)
        ps = wsMsgContent.split('Parameters[]:')[1].split('\n')[0]
        parameters = sm.getQueryStringParameters(ps)
        if 'set' in parameters:
            s = sm.setParameters(s, 'set='+parameters.get('set'))
        else:
            s = sm.setParameters(s, '')
        s = sm.setHeaders(s,'')
        return s

    def formatProcessorInfoRequest(self):
        s = sm.setResourcePath('/info')
        s = sm.setParameters(s, '')
        s = sm.setHeaders(s,'')
        return s

    def formatAuthRequestToProcessor(self, wsMsgContent):
        cardDetails = wsMsgContent.split('Parameters[]:')[1].split('\n')[0]
        s = sm.setResourcePath('/auth')
        s = sm.setParameters(s, cardDetails)
        s = sm.setHeaders(s,'')
        return s

    def getAuthOutcome(self, wsMsgContent):
        processorNumber = self.selectProcessor(wsMsgContent)
        address = self.findAddress(processorNumber)
        p_socket = io.establishConnection(address)
        s = self.formatAuthRequestToProcessor(wsMsgContent)
        responseFromProcessor = self.sendMessageAndGetResponse(p_socket, s)
        return responseFromProcessor

    def getProcessorsInfo(self):
        processorsAddresses = []
        notFoundAddresses = []
        for i in range(1, self.numberOfProcessors+1):
            try:
                p_address = self.findAddress(str(i))
                processorsAddresses.append(p_address)
            except ProcessorAddressNotFound as exc:
                print(exc.message)
                notFoundAddresses.append(i)
        if len(notFoundAddresses) > 0:
            print(f'\nNot found addresses: {notFoundAddresses}\n')
        unreachableProcessors = []
        processorsInfo = []
        for p_address in processorsAddresses:
            try:
                p_socket = io.establishConnection(p_address)
                message = self.formatProcessorInfoRequest()
                processorInfo = self.sendMessageAndGetResponse(p_socket, message)
                processorsInfo.append(processorInfo)
            except NetworkException as exc:
                print (exc.message)
                unreachableProcessors.append(p_address)
        if len(unreachableProcessors) > 0:
            print(f'\nUnreachable processors: {unreachableProcessors}\n')
        if len(processorsInfo) == 0:
            raise NetworkException('All the processors cannot be reached. ')
        processorsInfo.append('#')
        return (processorsInfo + unreachableProcessors)

    def getParameterRequestOutcome(self, wsMsgContent):
        parametersQueryString = wsMsgContent.split('Parameters[]:')[1].split('\n')[0]
        dictionary = sm.getQueryStringParameters(parametersQueryString)
        if 'proc' in dictionary:
            print(f'dictionary is {dictionary}')
            processorNumber = dictionary.get('proc')
            address = self.findAddress(processorNumber)
            p_socket = io.establishConnection(address)
            s = self.formatParameterRequest(wsMsgContent)
            responseFromProcessor = self.sendMessageAndGetResponse(p_socket, s)
            return responseFromProcessor
        else:
            raise ParametersNotCorrect('Missing proc parameter. ')

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
                return response.split('<STX>')[1].split('<ETX>')[0]
            else:
                raise NetworkException("The gateway couldn't receive the response correctly from the processor. ")

    def receiveMessageAndRespond(self, p_socket):
        message = io.readMessage(p_socket)
        if message != '<EOT>':
            content = message.split('<STX>')[1].split('<ETX>')[0]
            lrcReceived = message.split('<ETX>')[1]
            lrcCalculated = str(sm.getLRCvalueFromString(content))
            receivedEOT = False
            print(f'lrcCalculated = {lrcCalculated}\nlrcReceived = {lrcReceived}\n')
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
                html_page = self.handleMessageAndGetHTML(content) #here we call the logic to decide what to do
                lrcHTML = sm.getLRCvalueFromString(html_page)
                msgToSend = f'<STX>{html_page}<ETX>{lrcHTML}'
                io.writeMessage(p_socket,msgToSend)
                response = io.readMessage(p_socket)
                counter = 0
                while response != '<ACK>' and '<EOT>' not in response and counter<4:
                    counter += 1
                    io.writeMessage(p_socket, msgToSend)
                    response = io.readMessage(p_socket)
                if response != '<ACK>' and '<EOT>' not in response:
                    io.writeMessage(p_socket, '<EOT>')
                    raise NetworkException('The web server cannot receive data correctly.  ')
                elif '<EOT>' not in response:
                    endMessage = io.readMessage(p_socket) #waiting for <EOT>
            else:
                raise NetworkException("The gateway couldn't received the data correctly from the web server. ")

    def handleMessageAndGetHTML(self, msgContent):
        resourcePath = msgContent.split('ResourcePath:')[1].split('\n')[0]

        try:
            if resourcePath == '/auth':
                outcome = self.getAuthOutcome(msgContent)
                html = self.getUpdatedAuthHTML(outcome)
            elif resourcePath == '/index.html':
                outcome = self.getProcessorsInfo()
                html = self.getUpdatedProcessorsInfoHTML(outcome)
            elif resourcePath == '/status' or resourcePath == '/fl' or resourcePath == '/ul':
                outcome = self.getParameterRequestOutcome(msgContent)
                html = self.getUpdatedParameterRequestHTML(outcome)
            else:
                pass
        except (NetworkException, ProcessorAddressNotFound) as exc:
            html = io.readFile(os.path.curdir + '/error.html')
            newContent = '''<body>\n<div id="msg_instruction"> 409 Conflict </div>
                            <div id="details"> The gateway server cannot connect to the processor properly.
                                                Try again later. <br></div>'''
            newContent = newContent + f'<div id="specificError">Error details: {exc.message}</div>'
            v = html.split('<body>')
            html = v[0] + newContent + v[1]
        except ParametersNotCorrect as exc:
            html = io.readFile(os.path.curdir + '/error.html')
            newContent = '''<body>\n<div id="msg_instruction"> 400 Bad Request </div>
                            <div id="details"> The query string parameters are not correct.  <br></div>'''
            v = html.split('<body>')
            html = v[0] + newContent + v[1]
        return html

    def getUpdatedParameterRequestHTML(self, outcome):
        html_page = io.readFile(os.path.curdir + '/parametersResponse.html')
        v = html_page.split('<div id="outcome">')
        html_page = v[0] + '<div id="outcome">' + outcome + v[1]
        return html_page

    def getUpdatedAuthHTML(self, outcome):
        html_page = io.readFile(os.path.curdir + '/authResponse.html')
        v = html_page.split('<div id="outcome">')
        html_page = v[0] + '<div id="outcome">' + outcome + v[1]
        return html_page

    def getUpdatedProcessorsInfoHTML(self,processorsInfo):
        style = 'style = "margin-left: 2em; font-weight: normal; font-size: 22px;"'
        s = ''
        index = processorsInfo.index('#')
        for p_info in processorsInfo[:index]:
            s = s + f'<li {style} >{p_info}</li><br>\n'
        newContent = '<ul>\n' + s + '</ul>'

        if len(processorsInfo[index+1:])>0:
            s = f'<div {style}>The following processors could not be reached: {[i for i in processorsInfo[index+1:]]} </div>\n'
            newContent = newContent + s

        html_page = io.readFile(os.path.curdir + '/info.html')
        v = html_page.split('<div class="infoProcs">')
        html_page = v[0] + '<div class="infoProcs">' + newContent + v[1]
        return html_page
