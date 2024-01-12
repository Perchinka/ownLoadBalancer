from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread

class Proxy:
    def __init__(self, host: str, port: int) -> None:
        self.host = host
        self.port = port
        self.backend = None

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
        self.connect_to_backend()
        client_to_server = Thread(target=self.forward, args=(client_socket, self.backend)).start()
        server_to_client = Thread(target=self.forward, args=(self.backend, client_socket)).start()
        client_to_server.join()
        server_to_client.join()
        client_socket.close()
        self.backend.close()

    def forward(self, source: socket, dest: socket) -> None:
        while True:
            data = source.recv(1024)
            if not data:
                break
            dest.sendall(data)