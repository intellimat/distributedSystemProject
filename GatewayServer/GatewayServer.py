import socket
from threading import Thread

import controllerGatewayServer

class threadServer(Thread):
    def __init__(self,csocket):
        Thread.__init__(self)
        self.csocket = csocket
        self.host, self.port = self.csocket.getpeername()
        self.controller = controllerGatewayServer.Controller(csocket)
        print ('New server socket thread created. ')


    def run(self): #code run by each thread
        self.controller.parseRequest()

print('\n########## GATEWAY SERVER ##########')

# AF_INET means IPv4, SCOCK_STREM means TCP
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
IP = ''    #localhost but the server accepts requests from any client IP
PORT = int(input('\nSpecify a port (a integer higher than 10000): '))
s.bind((IP, PORT))
threads = []

while True:
    s.listen()
    print('\nServer is listening for new connections.\n')
    clientsocket, address = s.accept()
    print(f"\nConnection from {address} has been established!")
    print("Creating a thread to manage this connection.\n")
    newThread = threadServer(clientsocket)
    newThread.start()
    threads.append(newThread)

    threads = [t for t in threads if t.is_alive()]
    print(f"\nNumber of threads alive: {len(threads)}\n")

#for t in threads:
#    t.join()
