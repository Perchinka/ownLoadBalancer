import json
from typing import List
from ownloadbalancer.backend_server import BackendServer
from pydantic import BaseModel, ConfigDict

class Config(BaseModel):
        model_config = ConfigDict(arbitrary_types_allowed=True)

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

            servers = []
            for server in data["servers"]:
                try:
                    servers.append(BackendServer(server["host"], server["port"]))
                except KeyError:
                    raise ValueError("[-] Invalid server format")
            
            
            return Config(port = data["port"], servers = servers)
        
    except FileNotFoundError:
        raise FileNotFoundError(f"[-] Config file {config_file} not found")
    
    except json.decoder.JSONDecodeError:
        raise ValueError("[-] Invalid JSON file")
