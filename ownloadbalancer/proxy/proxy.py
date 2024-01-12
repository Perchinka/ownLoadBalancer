from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread, Lock

class Proxy:
    def __init__(self, host: str, port: int) -> None:
        self.host = host
        self.port = port
        self.backend = None
        self.connections = 0
        self.lock = Lock()

    def is_alive(self) -> bool:
        try:
            self.connect_to_backend()
            self.backend.close()
            return True
        except Exception as e:
            print(f"[-] {e}")
            return False
    
    def connect_to_backend(self) -> None:
        self.backend = socket(AF_INET, SOCK_STREAM)
        self.backend.connect((self.host, self.port))

    def start_proxy(self, client_socket: socket) -> None:
        if not self.is_alive():
            return
        
        self.connect_to_backend()
        client_to_server = Thread(target=self.forward, args=(client_socket, self.backend))
        server_to_client = Thread(target=self.forward, args=(self.backend, client_socket))
        client_to_server.start()
        server_to_client.start()
        client_to_server.join()
        server_to_client.join()
        client_socket.close()
        self.backend.close()

    def forward(self, source: socket, dest: socket) -> None:
        with self.lock:
            self.connections += 1
        try:
            while True:
                data = source.recv(1024)
                if len(data) == 0:
                    break
                print(f"sending data from ]{source.getpeername()}] to [{dest.getpeername()}]")
                dest.send(data)
        finally:
            with self.lock:
                self.connections -= 1
    