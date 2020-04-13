import socket
import os, sys
import pathlib

pathRepo = os.path.dirname(os.path.dirname(os.getcwd()))
sys.path.insert(1, pathRepo)    #We are setting the path to import the modules

from distributedSystemProject.utils import inputOutput as io
from distributedSystemProject.utils import stringManager as sm
from distributedSystemProject.utils.Exception import NetworkException, ParametersNotCorrect

from random import randint
from datetime import date, datetime

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
                while response != '<ACK>' and '<EOT>' not in response and counter<4:
                    counter += 1
                    io.writeMessage(p_socket, msgToSend)
                    response = io.readMessage(p_socket)
                if response != '<ACK>' and '<EOT>' not in response:
                    io.writeMessage(p_socket, '<EOT>')
                    raise NetworkException('The gateway cannot receive data correctly. ')
                elif '<EOT>' not in response:
                    endMessage = io.readMessage(p_socket) #waiting for <EOT>
            else:
                raise NetworkException("The processor couldn't receive data correctly from the Gateway. ")

    def handleMessageAndGetResponse(self, msgContent):
        resourcePath = msgContent.split('ResourcePath:')[1].split('\n')[0]
        print(f'ResourcePath: {resourcePath}')

        if resourcePath == '/auth':
            outcome = self.getAuthOutcome(msgContent)
            return outcome
        elif resourcePath == '/info':
            outcome = self.getProcParameters()
            return outcome
        elif resourcePath == '/status' or resourcePath == '/ul' or resourcePath == '/fl':
            outcome = self.getParameterRequestOutcome(msgContent)
            return outcome
        else:
            return 'ERROR'

    def getParameterRequestOutcome(self, msgContent):
        parameter = msgContent.split('ResourcePath:/')[1].split('\n')[0]
        queryStringParameters = msgContent.split('Parameters[]:')[1].split('\n')[0]
        dictionary = sm.getQueryStringParameters(queryStringParameters)
        if 'set' in dictionary:
            value = dictionary.get('set')
            if parameter == 'fl':
                parameter = 'floor'
            elif parameter == 'ul':
                parameter = 'upper'
            self.setProcParameter(f'{parameter}={value}')
            return f'Parameter {parameter} has been updated with the value {value}.'
        else:
            value = self.getParameterValue(parameter)
            return f'{parameter}={value}'

    def getAuthOutcome(self, msgContent):
        d = date.today().strftime("%B %d, %Y")

        if self.getParameterValue('status') == 'ON' or self.getParameterValue('status') == 'on':
            expDate = msgContent.split('Parameters[]:')[1].split('\n')[0].split('#')[-2]
            amount = int(msgContent.split('Parameters[]:')[1].split('\n')[0].split('#')[-1])
            if self.isExpDateValid(expDate):
                floorLimit = int(self.getParameterValue('floor'))
                upperLimit = int(self.getParameterValue('upper'))
                if amount > floorLimit and amount<upperLimit:
                    outcome = f'<font color="green"> ACCEPTED </font> <br>AuthCode: {randint(0,1000)} <br>Amount: {amount} euro <br>Date: {d}'
                else:
                    outcome = f'<font color="red"> REFUSED </font> <br>AuthCode: {randint(0,1000)} <br>Amount: {amount} euro <br>Date: {d}'
            else:
                outcome = f'<font color="red"> REFUSED </font> <br>AuthCode: {randint(0,1000)} <br>Amount: {amount} euro <br>Date: {d} <br> The card provided has expired. '
        else:
            outcome = f'The processor is not available for processing your payment request. '
        return outcome

    def getParameterValue(self,parameter): #parameter must be 'status', 'floor' or 'upper'
        f = self.getProcParameters()
        if parameter == 'fl':
            parameter = 'floor'
        elif parameter == 'ul':
            parameter = 'upper'
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
        after = v[1].split('\n', 1)[1]
        middle = parameter + '\n'
        s = before + middle + after
        io.writeFile(filePath, s)

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

    def isExpDateValid(self, expDate): #checks if the expiration date is valid
        if '/' in expDate:
            v = expDate.split('/')
            expMonth = int(v[0])
            expYear = int(str(v[1])[2:4])
            currentMonth = datetime.now().month
            currentYear = int(str(datetime.now().year)[2:4]) #casting
            if expYear < currentYear:
                return False
            elif expYear == currentYear and expMonth < currentMonth:
                return False
            return True
        else:
            raise ParametersNotCorrect('Invalid date format. The date format must be month/year (for instance, 02/22). ')
