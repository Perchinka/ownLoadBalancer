import json
from typing import List
from ownloadbalancer.backend_server import BackendServer
from pydantic import BaseModel, ConfigDict
from ownloadbalancer.algorithms.algorithms import algorithms, Algorithm

class Config(BaseModel):
        model_config = ConfigDict(arbitrary_types_allowed=True)

        port: int
        servers: List[BackendServer]
        algorithm: Algorithm = algorithms["ROUND_ROBIN"]()
        
def load_config(config_file: str) -> Config:
    try:
        with open(config_file) as config:
            data = json.load(config)

            try:
                if len(data["servers"]) == 0:
                    raise ValueError("[-] Server list is empty")
            except KeyError:
                raise ValueError("[-] No servers specified")

            servers = []
            for server in data["servers"]:
                try:
                    servers.append(BackendServer(server["host"], server["port"]))
                except KeyError:
                    raise ValueError("[-] Invalid server format")


            if "algorithm" not in data:
                algorithm = algorithms["ROUND_ROBIN"]()
            elif data["algorithm"].upper() in algorithms:
                algorithm = algorithms[data["algorithm"].upper()]()
            else:
                raise ValueError("[-] Invalid algorithm")

            return Config(port = data["port"], servers = servers, algorithm = algorithm)
        
    except FileNotFoundError:
        raise FileNotFoundError(f"[-] Config file {config_file} not found")
    
    except json.decoder.JSONDecodeError:
        raise ValueError("[-] Invalid JSON file")
