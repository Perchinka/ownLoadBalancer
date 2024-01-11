import pytest
import asyncio
from ownloadbalancer.listener import Listener
import json

@pytest.fixture
def dummy_client():
    return asyncio.open_connection(host="127.0.0.1", port=8080)

@pytest.fixture
def config_file(tmpdir):
    config_data = {
        "port": 8080,
        "log_file": "app.log",
        "server_list": ["server1", "server2"]
    }
    config_path = tmpdir.join("config.json")
    config_path.write(json.dumps(config_data))
    return str(config_path)

def test_listener_with_valid_config(config_file):
    listener = Listener(config_file=config_file)
    
    assert listener.port == 8080
    assert listener.log_file == "app.log"
    assert listener.server_list == ["server1", "server2"]

def test_listener_with_invalid_config(config_file):
    # Modify the configuration data to make it invalid
    with open(config_file, "w") as file:
        file.write("invalid_json_data")
    
    with pytest.raises(Exception):  # Adjust the exception type as needed
        listener = Listener(config_file=config_file)

def test_listener_with_nonexistent_config():
    with pytest.raises(FileNotFoundError):
        listener = Listener(config_file="nonexistent_config.json")
    
