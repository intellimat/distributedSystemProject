import json
from distributedSystemProject.utils.Exception import ParametersNotCorrect
def calculate_LRC(data):
    lrc = 0x00
    for element in data:
        lrc^=element

    return lrc

#lrc = calculate_LRC([ord('H'),ord('E'),ord('L'),ord('L'),ord('O')])
#print lrc

def getLRCvalueFromString(s): #s is the string
    l = [ord(i) for i in s]
    return calculate_LRC(l)

def isLRC_ok(msgFromProc):  #deprecated
    v = msgFromProc.split('<STX>')
    vu = v[1].split('<ETX>')
    answer = vu[0]
    lrc_fromProc = int(vu[1])
    calculated_lrc = getLRCvalueFromString(answer)
    print(f'Calculated_LRC = {calculated_lrc}\nReceived_LRC = {lrc_fromProc}')
    return calculated_lrc == lrc_fromProc

def getQueryStringParameters(url): #returns a dictionary with all the parameters -> key : value
    try:
        v = url.split('?')
        v = v[1].split('&')
        d = {}
        for i in v:
            u = i.split('=')
            d[u[0]] = u[1]
        return d
    except ValueError as exc:
        raise ParametersNotCorrect()

def setContentLength(msg, msgLength):
    return msg + f'\nContent-Length: {msgLength}'

def setContentType(msg, type):
    return msg + f'\nContent-Type: {type}'

def setConnection(msg, connection):
    return msg + f'\nConnection: {connection}'

def setCode(msg, code):
    return msg + f' {str(code)}'

def setMessageAnswer(msg, answer):
    return msg + f' {answer}'

''' Helper methods for setting the message correctly according to the protocol '''
def setResourcePath(path):
    return f'ResourcePath:{path}'

def setParameters(msg, params):
    return msg + f'\nParameters[]:{params}'

def setHeaders(msg, headers):
    return msg + f'\nHeaders[]:{headers}'
