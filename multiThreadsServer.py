import sys
import socket
from threading import Thread
from os import curdir, sep

class threadServer(Thread):
    def __init__(self,csocket):
        Thread.__init__(self)
        self.csocket = csocket

        print (f'New server socket thread created')


    def run(self):
        host, port = self.csocket.getpeername()


        data = self.csocket.recv(4092)
        msg = data.decode("utf-8")
        print(f"\nServer received the message:\n\n\n '{msg}' \n\n\nfrom {host} on port {port}")
        f = open(curdir + '/index.html')
        page = f.read()
        f.close()
        self.csocket.send(bytes(page,"utf-8"))
        self.csocket.close()        #closes the TCP connection
        print(f'\nThe connection to {host} on port {port} has been closed by the server')




# AF_INET means IPv4, SCOCK_STREM means TCP
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
IP = '127.0.0.1'    #localhost
PORT = int(input('\nSpecify a port (a integer higher than 10000): '))
s.bind((IP, PORT))
threads = []

while True:
    s.listen()
    print('\nServer is listening for new connections')
    clientsocket, address = s.accept()
    print(f"\nConnection from {address} has been established!")
    print(f"Creating a thread to manage this connection")
    newThread = threadServer(clientsocket)
    newThread.start()
    threads.append(newThread)

    threads = [t for t in threads if t.is_alive()]
    print(f"\nNumber of threads alive: {len(threads)}")

#for t in threads:
#    t.join()
