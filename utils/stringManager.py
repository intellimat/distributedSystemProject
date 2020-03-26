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

s = input('Insert a string: \n')
valueLRC = getLRCvalueFromString(s)
print(f'LRC value is: {valueLRC}')
