import socket
import os, sys

pathRepo = os.path.dirname(os.path.dirname(os.getcwd()))
sys.path.insert(1, pathRepo)

from distributedSystemProject.utils import inputOutput as io

class Controller(object):
    def __init__(self,csocket):
        self.csocket = csocket
        self.host, self.port = self.csocket.getpeername()

    def parseRequest(self):
        msgFromClient = self.readRequest(self.csocket)
        print(f"\nServer received the message:\n\n\n '{msgFromClient}' \n\n\nfrom {self.host} on port {self.port}\n\n\n")
        io.writeResponse(self.csocket, 'Thank you for the POST data.')
        ''' here goes all the logic of the gateway server '''


    def closeConnection(self): #closes the TCP connection
        self.csocket.close()
        print(f'\nThe connection to {self.host} on port {self.port} has been closed by the server')


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
