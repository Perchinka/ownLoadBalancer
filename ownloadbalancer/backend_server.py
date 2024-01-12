from typing import List
from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread

# TODO: Add logging
# TODO: Add cmd line args
# TODO: Rewrite to HTTP data format
class BackendServer:
    '''Server accepting connections from load balancer and proceed them'''
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.thread = None

    def respond(self, data: str) -> str:
        return f"Hello from server [{self.host}:{self.port}]\n"

    def run(self):
        try:
            with socket(AF_INET, SOCK_STREAM) as s:
                s.bind((self.host, self.port))
                s.listen()
                print(f"[+] Server [{self.host}:{self.port}] is running")
                while True:
                    conn, addr = s.accept()
                    with conn:
                        print(f"[+] Connected to server [{self.host}:{self.port}]:", addr)
                        data = conn.recv(1024).decode()
                        print(f"[+] Received data from {addr}:", data)
                        response = self.respond(data)
                        conn.send(response.encode())
        except Exception as e:
            print(f"[-] Error: {e}")
        except KeyboardInterrupt:
            print("[!] Server is stopping")
        finally:
            s.close()

        
if __name__ == "__main__":
    HOST = "127.0.0.1"
    PORT = 1337 # Will be cmd line arg

    server = BackendServer(HOST, PORT)
    server.run()

    