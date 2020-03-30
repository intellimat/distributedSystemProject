import json
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
    return calculated_lrc == lrc_fromProc

def getQueryStringParameters(url): #returns a dictionary with all the parameters -> key : value
    v = url.split('?')
    v = v[1].split('&')
    d = {}
    for i in v:
        u = i.split('=')
        d[u[0]] = u[1]
    return d
