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
        msgFromClient = io.readMessage(self.csocket)
        print(f"\nServer received the message:\n\n\n '{msgFromClient}' \n\n\nfrom {self.host} on port {self.port}\n\n\n")

        ''' here goes all the logic of the processor '''
        path = self.getPath(msgFromClient)
        print(f'\n\nPath of the request is {path}\n\n')

        if not self.isCorrectPath(path):
            pass

        elif path == '/info':
            self.sendProcParameters()

        else:
            pass

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
