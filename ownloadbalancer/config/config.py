import json
from typing import Dict

def load_config(config_file="config.json") -> Dict:
    with open(config_file) as config:
        return json.load(config)