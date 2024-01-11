import json
from typing import Dict, List
from ownloadbalancer.backend_server import BackendServer
from pydantic import BaseModel

class Config(BaseModel):
        port: int
        servers: List[BackendServer]

def load_config(config_file: str) -> Config:
    try:
        with open(config_file) as config:
            data = json.load(config)

            try:
                if len(data["servers"]) == 0:
                    raise ValueError("[-] Server list is empty")
            except KeyError:
                raise ValueError("[-] No servers specified")

            for server in data["servers"]:
                try:
                    server["host"]
                    server["port"]
                except KeyError:
                    raise ValueError("[-] Invalid server format")
            
            return Config(port = data["port"], servers = data["servers"])
        
    except FileNotFoundError:
        raise FileNotFoundError(f"[-] Config file {config_file} not found")
    

if __name__ == "__main__":
    config = load_config("config.json")
    print(config.port)
    print(config.servers)
    for server in config.servers:
        print(type(server))