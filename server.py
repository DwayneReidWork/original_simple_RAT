import socket
import threading

from .server_client import Client

class Server():
    def __init__(self, bind_host: str, bind_port:int):
        self.__bind_host = bind_host
        self.__bind_port = bind_port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        #self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)

    def start(self):
        self.sock.bind((self.__bind_host, self.__bind_port))
        self.sock.listen()
        print(f'Listening on {self.__bind_host}:{self.__bind_port}')

        while True:
            try:
                client_sock, client_addr = self.sock.accept()
                print(f'Connection form: {client_addr}')
                c = Client(client_sock, client_addr)
                c.start()
            except:
                print('Failed to accept.')
                break

        self.sock.close()
        self.sock = None
        print('Shutdown.')
        