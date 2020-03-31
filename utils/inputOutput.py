''' Helper module '''
import socket
pathRepo = os.path.dirname(os.path.dirname(os.getcwd()))
sys.path.insert(1, pathRepo)

from distributedSystemProject.utils import stringManager as sm


def readMessage(sock): #reads the message coming from the client
    rawData = sock.recv(4092)
    decodedData = rawData.decode("utf-8")
    host, port = sock.getpeername()
    print(f"Received the message:\n'{decodedData}' \nfrom {host} on port {port}\n\n")
    return decodedData

def readFile(path): #reads a file stored in a directory specified by the path argument
    f = open(path)
    content = f.read()
    f.close()
    if len(content) < 100:
        print(f'\nRead file:\n{content}\n\n')
    return content

def writeFile(path, content):
    f = open(path, 'w')
    f.write(content)
    f.close()
    print(f'Written file with this content:\n {content}')


def writeMessage(sock, data): #writes a response to the client
    host, port = sock.getpeername()
    sock.send(bytes(data,"utf-8"))
    print(f'Sent:\n{data} to {host} on port {port}\n')


def closeConnection(socket): #closes the TCP connection
    host, port = socket.getpeername()
    socket.close()
    print(f'\nThe connection to {host} on port {port} has been closed by the server')

def establishConnection(address):
    print(f'Trying to connect to {address}\n')
    IP = address[0]
    PORT = address[1]
    sock = connectTo(IP, PORT)
    writeMessage(sock,'<ENQ>')
    response = readMessage(sock)
    counter = 1
    while response != '<ACK>' and counter<3:
        counter += 1
        writeMessage(sock,'<ENQ>')
        response = readMessage(sock)
    if response != '<ACK>':
        raise Exception(f'Impossible to establish connection with {address}')
    print(f'Connection to {address} established. ')
    return sock

def sendMessage(p_socket, message):
    lrc = sm.getLRCvalueFromString(message)
    s = '<STX>' + message + '<ETX>' + str(lrc)
    writeMessage(p_socket, s)
    response = readMessage(p_socket)
    counter = 0
    while response != '<ACK>' and counter<4:
        counter += 1
        writeMessage(p_socket, s)
        response = readMessage(p_socket)
    if response != '<ACK>':
        writeMessage(p_socket, '<EOT>')
        raise Exception('The addressee cannot receive data correctly.  ')
    else: #<ACK> for the data sent
        response = readMessage(p_socket) #the answer
        receivedEOT = False
        while not receivedEOT and not sm.isLRC_ok(response):
            writeMessage(p_socket, '<NACK>')
            response = readMessage(p_socket)
            if response == '<EOT>':
                receivedEOT = True
        if receivedEOT == False: #means that I received correctly the response
            writeMessage(p_socket,'<ACK>')
            writeMessage(p_socket,'<EOT>')
        else:
            raise Exception("I couldn't receive the response correctly. ")

def receiveMessageAndRespond(p_socket):
    message = readMessage(p_socket)
    if message != '<EOT>':
        content = message.split('<STX>')[1].split('<ETX>')[0]
        lrcReceived = message.split('<ETX>')[1]
        lrcCalculated = sm.getLRCvalueFromString(content)
        receivedEOT = False
        while not receivedEOT and (lrcCalculated != lrcReceived):
            writeMessage(p_socket, '<NACK>')
            message = readMessage(p_socket)
            if message == '<EOT>':
                receivedEOT = True
            else:
                lrcReceived = message.split('<ETX>')[1]
                lrcCalculated = sm.getLRCvalueFromString(content)
        if not receivedEOT:
            writeMessage(p_socket,'<ACK>')
            answer = ''' we got the answer by calling some methods '''
            writeMessage(p_socket,answer)
            response = readMessage(p_socket)
            counter = 0
            while response != '<ACK>' and counter<4:
                counter += 1
                writeMessage(p_socket, answer)
                response = readMessage(p_socket)
            if response != '<ACK>':
                writeMessage(p_socket, '<EOT>')
                raise Exception('The addressee cannot receive data correctly.  ')
            else:
                endMessage = readMessage(p_socket) #waiting for <EOT>
        else:
            raise Exception("I couldn't received the data. ")






def connectTo(IP, PORT):
    # AF_INET means IPv4, SCOCK_STREM means TCP
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((IP, PORT))
    return s
