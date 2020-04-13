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

def isLRC_ok(msgFromProc):
    v = msgFromProc.split('<STX>')
    vu = v[1].split('<ETX>')
    answer = vu[0]
    lrc_fromProc = int(vu[1])
    calculated_lrc = getLRCvalueFromString(answer)
    print(f'Calculated_LRC = {calculated_lrc}\nReceived_LRC = {lrc_fromProc}')
    return calculated_lrc == lrc_fromProc

def getQueryStringParameters(url): #returns a dictionary with all the parameters -> key : value
    try:
        d = {}
        v = url.split('?')
        if len(v)>=2 and '&' in v[1]:
            v = v[1].split('&')
            for i in v:
                u = i.split('=')
                d[u[0]] = u[1]
        elif '&' in v[0]:
            v = v[0].split('&')
            for i in v:
                u = i.split('=')
                d[u[0]] = u[1]
        elif '=' in v[0]:
            u = v[0].split('=')
            d[u[0]] = u[1]
        return d
    except (ValueError,IndexError) as exc:
        raise ParametersNotCorrect(str(exc))

''' This methods down here help to format correctly the http requests. '''
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

def setServer(msg, server):
    return msg + f'\nServer: {server}'

''' Helper methods for setting the message correctly according to the protocol implemented. '''
def setResourcePath(path):
    return f'ResourcePath:{path}'

def setParameters(msg, params):
    return msg + f'\nParameters[]:{params}'

def setHeaders(msg, headers):
    return msg + f'\nHeaders[]:{headers}'
