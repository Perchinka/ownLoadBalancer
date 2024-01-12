from typing import Any
from ownloadbalancer.config.config import Config, load_config
from typing import List, Dict
from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread


class Listener:
    def __init__(self, config_file: str = 'config.json') -> None:
        self.config: Config = load_config(config_file)
        self.port: int = self.config.port
        self.servers: List = self.config.servers

    def on_connect(self, socket: socket) -> None:
        pass
        # backend = choose(self.servers)
        # backend.rev_proxy(socket)
        

    def start(self) -> None:
        proxy_threads: List[Thread] = []
        sock = socket(AF_INET, SOCK_STREAM)
        try:
            sock.bind(("127.0.0.1", self.port))
            sock.listen(1000)
            print(f"[+] Listening on port {self.port}")

            # TODO: Add stop method/flag
            while True:
                client, client_addr = sock.accept()
                
                # TODO: Add different algorithm for choosing backend server (Round Robin, Least Connections, Weighted Round Robin (mb))

                print(f"[+] Accepted connection from {client_addr[0]}:{client_addr[1]}")
                proxy_thread = Thread(target=self.on_connect, args=(client,))
                proxy_thread.start()
                proxy_threads.append(proxy_thread)
        except KeyboardInterrupt:
            print("[!] Shutting down")
        except Exception as e:
            print(f"[-] Error: {e}")
        finally:
            sock.close()
            for proxy_thread in proxy_threads:
                proxy_thread.join()

