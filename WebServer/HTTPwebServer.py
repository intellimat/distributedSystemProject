import sys
import socket
from threading import Thread

import controllerHTTPwebServer

class threadServer(Thread):
    def __init__(self,csocket):
        Thread.__init__(self)
        self.csocket = csocket
        self.host, self.port = self.csocket.getpeername()
        self.controller = controllerHTTPwebServer.Controller(csocket)
        self.controller.gatewayIP = gatewayIP
        self.controller.gatewayPORT = gatewayPORT
        print(f'New server socket thread created.')

    def run(self): #code run by each thread
        self.controller.parseRequest()

# AF_INET means IPv4, SCOCK_STREM means TCP
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
IP = ''    #localhost
PORT = int(input('\nSpecify a port for the HTTP web server (an integer higher than 10000): '))
s.bind((IP, PORT))

threads = []

gatewayIP = input('\nType gatewayIP: ')
gatewayPORT = int(input('\nType gatewayPORT: '))

while True:
    s.listen()
    print('\nServer is listening for new connections.\n')
    clientsocket, address = s.accept()
    print(f"\nConnection from {address} has been established!\n")
    print(f"Creating a thread to manage this connection.\n")
    newThread = threadServer(clientsocket)
    newThread.start()
    threads.append(newThread)

    threads = [t for t in threads if t.is_alive()]
    print(f"\nNumber of threads alive: {len(threads)}\n")
#for t in threads:
    #t.join()
