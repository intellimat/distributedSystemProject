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
        print('MANAGE AUTH REQUEST METHOD')
        #Read value and check wether to accept or refuse the request
        io.writeMessage(self.csocket, 'ACCEPTED')
        gatewayResponse = io.readMessage(p_socket)
        counter = 1
        while gatewayResponse != '<ACK>' and counter<4:
            counter += 1
            self.sendAuthToProcessor(p_socket, msgFromGateway)
            gatewayResponse = io.readMessage(p_socket)
        if gatewayResponse != '<ACK>':
            io.writeMessage('<EOT>')
            io.closeConnection(self.csocket)
        else: #<ACK> for the data sent
            io.readMessage(self.csocket) #expecting <EOT>


    def getProcParameters(self):
        basicPath = pathlib.Path.cwd()
        filePath = pathlib.Path(basicPath, 'config.txt')
        f = io.readFile(filePath)
        return f

    def sendProcParameters(self):
        params = self.getProcParameters()
        io.writeMessage(self.csocket, params)

    def setProcParameters(self, id, status, floor, upper):
        pass

    def isCorrectPath(self, path):
        if path == '/info':
            return True
        return False

    def getPath(self,clientMsg):
        path = clientMsg.split()[1]
        return path
