import socket
import os, sys
import json
import pathlib

pathRepo = os.path.dirname(os.path.dirname(os.getcwd()))
sys.path.insert(1, pathRepo)

from distributedSystemProject.utils import inputOutput as io
from distributedSystemProject.utils import stringManager as sm
from distributedSystemProject.utils.Exception import NetworkException
from random import randint
from datetime import date

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


    def acceptConnection(self):
        msgFromWs = io.readMessage(self.csocket)
        while msgFromWs != '<ENQ>' and msgFromWs != '<EOT>':
            msgFromWs = io.readMessage(self.csocket)
        if msgFromWs == '<ENQ>':
            io.writeMessage(self.csocket, '<ACK>')
        else:
            raise NetworkException('Impossible to accept the gateway connection. ')

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
                response = self.handleMessageAndGetResponse(content)
                lrcResponse = sm.getLRCvalueFromString(response)
                msgToSend = f'<STX>{response}<ETX>{lrcResponse}'
                io.writeMessage(p_socket,msgToSend)
                response = io.readMessage(p_socket)
                counter = 0
                while response != '<ACK>' and counter<4:
                    counter += 1
                    io.writeMessage(p_socket, msgToSend)
                    response = io.readMessage(p_socket)
                if response != '<ACK>':
                    io.writeMessage(p_socket, '<EOT>')
                    raise NetworkException('The gateway cannot receive data correctly.  ')
                else:
                    endMessage = io.readMessage(p_socket) #waiting for <EOT>
            else:
                raise NetworkException("The processor couldn't receive data correctly from the Gateway")

    def handleMessageAndGetResponse(self, msgContent):
        resourcePath = msgContent.split('ResourcePath:')[1].split('\n')[0]
        print(f'ResourcePath: {resourcePath}')

        if resourcePath == '/auth':
            outcome = self.getAuthOutcome(msgContent)
            return outcome
        elif resourcePath == '/info':
            outcome = self.getProcParameters()
            return outcome

        else:
            return 'ramo else'
            pass

    def getAuthOutcome(self, msgContent):
        d = date.today().strftime("%B %d, %Y")

        if self.getParameterValue('status') == 'ON':
            amount = int(msgContent.split('Parameters[]:')[1].split('\n')[0])
            floorLimit = int(self.getParameterValue('floor'))
            upperLimit = int(self.getParameterValue('upper'))
            if amount > floorLimit and amount<upperLimit:
                outcome = f'Accepted. AuthCode:{randint(0,1000)}. Amount: {amount} euro. Date: {d}'
            else:
                outcome = f'Refused. AuthCode:{randint(0,1000)}. Amount: {amount} euro. Date: {d}'
        else:
            outcome = f'The processor status is OFF. '
        return outcome

    def getParameterValue(self,parameter): #parameter must be 'status', 'floor' or 'upper'
        f = self.getProcParameters()
        value = f.split(parameter + '=')[1].split('\n')[0]
        return value


    def getProcParameters(self):
        basicPath = pathlib.Path.cwd()
        filePath = pathlib.Path(basicPath, 'config.txt')
        f = io.readFile(filePath)
        return f

    def setProcParameter(self, parameter):  #parameter is something like this 'status=OFF'
        basicPath = pathlib.Path.cwd()
        filePath = pathlib.Path(basicPath, 'config.txt')
        f = io.readFile(filePath)
        defParameter = parameter.split('=')[0]
        v = f.split(defParameter)
        before = v[0]
        after = v[1].split('\n')[1]
        middle = parameter + '\n'
        s = before + middle + after
        io.writeFile(filePath, s)

        '''
        defParameter = parameter.split('=')[0]
        if defParameter == 'id':
            status = f'status={self.getParameterValue('status')}'
            floor = f'floor={self.getParameterValue('floor')}'
            upper =f'upper={self.getParameterValue('upper')}'
            s = f'{parameter}\n{status}{floor}{upper}'
            io.writeFile(filePath, s)

        elif defParameter == 'status':
            pass
        elif defParameter == 'floor':
            pass
        elif defParameter == 'upper':
            pass
        '''

    def isPathCorrect(self, msgFromClient):
        accessiblePaths = { '0': '/auth',
                            '1': '/status',
                            '2': '/fl',
                            '3': '/ul',
                            '4': '/info'}

        path = self.getPath(msgFromClient).split('?')[0]
        for n in accessiblePaths:
            if accessiblePaths.get(n) == path:
                return True
        return False

    def getPath(self,clientMsg):
        path = clientMsg.split()[1]
        return path
