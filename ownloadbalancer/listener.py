from typing import Any
from ownloadbalancer.config.config import load_config
from typing import List, Dict


class Listener:
    def __init__(self, config_file: str = "config.json") -> None:
        self.config: Dict = load_config(config_file)
        self.port: int = self.config["port"]
        self.log_file: str = self.config["log_file"]
        self.server_list: List = self.config["server_list"]

    