from ownloadbalancer.config.config import Config, load_config
from ownloadbalancer.algorithms.algorithms import choose, Algorithm
from ownloadbalancer.proxy.proxy import Proxy

from typing import List

from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread


class Listener:
    def __init__(self, config_file: str = 'config.json') -> None:
        self.config: Config = load_config(config_file)
        self.port: int = self.config.port
        self.servers: List = self.config.servers
        self.algorithm: Algorithm = self.config.algorithm
        

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
                print(f"[+] Accepted connection from {client_addr[0]}:{client_addr[1]}")
                
                server = choose(self.servers, self.algorithm)
                proxy = Proxy(server.host, server.port)
                
                proxy_thread = Thread(target=proxy.start_proxy, args=(client,))
                proxy_thread.start()
                proxy_threads.append(proxy_thread)
        except KeyboardInterrupt:
            print("[!] Shutting down")
        except Exception as e:
            print(f"[-] Error in **Listener**: {e}")
        finally:
            sock.close()
            for proxy_thread in proxy_threads:
                proxy_thread.join()


if __name__ == "__main__":
    listener = Listener()
    listener.start()
