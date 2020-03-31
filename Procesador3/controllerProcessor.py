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

    def manageClientInteraction(self):
        msgFromGateway = io.readMessage(self.csocket)
        if msgFromGateway == '<ENQ>':
            io.writeMessage(self.csocket, '<ACK>')
            msgFromGateway = io.readMessage(self.csocket)
            if msgFromGateway == '<EOT>':
                print('Connection ended by the Gateway server without sending data. ')
            else:
                counter=1
                lrc_correct = sm.isLRC_ok(msgFromGateway)
                print(f'LRC value = {lrc_correct}')
                while (not lrc_correct) and counter<4:
                    counter+=1
                    io.writeMessage(self.csocket, '<NACK>')
                    msgFromGateway = io.readMessage(self.csocket)
                    lrc_correct = sm.isLRC_ok(msgFromGateway)
                if lrc_correct:
                    io.writeMessage(self.csocket, '<ACK>')
                    path = msgFromGateway.split('ResourcePath:')[1].split('\n')[0]
                    if path == '/auth':
                        try:
                            self.manageAuthRequest(msgFromGateway)
                        except Exception as exc:
                            print(f'Exception: {exc}')

        else:
            io.writeMessage(self.csocket,'<NACK>')
            io.writeMessage(self.csockeet, '<EOT>')

    def manageAuthRequest(self, msgFromGateway):
        #Read value and check wether to accept or refuse the request
        outcome = 'ACCEPTED'
        lrc = sm.getLRCvalueFromString(outcome)
        s = f'<STX>{outcome}<ETX>{lrc}'
        io.writeMessage(self.csocket, s)
        gatewayResponse = io.readMessage(self.csocket)
        counter = 1
        while gatewayResponse != '<ACK>' and counter<4:
            counter += 1
            io.writeMessage(self.csocket, 'ACCEPTED')
            gatewayResponse = io.readMessage(self.csocket)
        if gatewayResponse != '<ACK>':
            io.writeMessage(self.csocket, '<EOT>')
            io.closeConnection(self.csocket)
        else: #<ACK> for the data sent
            io.readMessage(self.csocket) #expecting <EOT>

    def getParameterValue(self,parameter):
        f = getProcParameters()
        value = f.split(parameter + '=')[1].split('\n')[0]
        return value


    def getProcParameters(self):
        basicPath = pathlib.Path.cwd()
        filePath = pathlib.Path(basicPath, 'config.txt')
        f = io.readFile(filePath)
        return f

    def sendProcParameters(self):
        params = self.getProcParameters()
        io.writeMessage(self.csocket, params)

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
                        '3': '/ul'}

    path = self.getPath(msgFromClient).split('?')[0]
    for n in accessiblePaths:
        if accessiblePaths.get(n) == path:
            return True
    return False

    def getPath(self,clientMsg):
        path = clientMsg.split()[1]
        return path
