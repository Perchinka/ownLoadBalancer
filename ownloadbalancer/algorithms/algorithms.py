from enum import Enum
from typing import List
from ownloadbalancer.backend_server import BackendServer
import random
from abc import ABC, abstractmethod


# Abstract class for all algorithms
class Algorithm(ABC):
    def __init__(self) -> None:
        self.index = 0

    @abstractmethod
    def choose(self) -> BackendServer:
        raise NotImplementedError    


class RoundRobin(Algorithm):
    def __init__(self) -> None:
        super().__init__()

    def choose(self, servers: List[BackendServer]) -> BackendServer:
        server = servers[self.index]
        self.index = (self.index + 1) % len(servers)
        return server


class LeastConnection(Algorithm):
    def __init__(self) -> None:
        super().__init__()

    def choose(self, servers: List[BackendServer]) -> BackendServer:
        servers = sorted(servers, key=lambda server: server.connections)
        return servers[0]
    

class Random(Algorithm):
    def __init__(self) -> None:
        super().__init__()

    def choose(self, servers: List[BackendServer]) -> BackendServer:
        return random.choice(servers)
    


algorithms = {
    "ROUND_ROBIN": RoundRobin,
    "LEAST_CONNECTION": LeastConnection,
    "RANDOM" :Random
}

def choose(servers: List[BackendServer], algorithm: Algorithm = algorithms["RANDOM"]) -> BackendServer:
    return algorithm.choose(servers)