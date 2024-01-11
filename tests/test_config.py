import pytest
from ownloadbalancer.config.config import load_config
from ownloadbalancer.backend_server import BackendServer
import json


@pytest.fixture
def config_file(tmpdir):
    config_data = {
        "port": 16320,
        "servers": [
            {
                "host": "127.0.0.1",
                "port": 1337
            }, 
            {
                "host": "127.0.0.1",
                "port": 1338
            }
        ]
    }

    config_path = tmpdir.join("config.json")
    config_path.write(json.dumps(config_data))
    return str(config_path)


def test_config_should_load_config_file(config_file):
    config = load_config(config_file)
    assert config.port == 16320

    
def test_config_should_raise_error_if_no_config_file():
    with pytest.raises(FileNotFoundError):
        config = load_config("nonexistent_config.json")


def test_config_should_raise_error_if_config_file_is_invalid(tmpdir):
    config_path = tmpdir.join("config.json")
    config_path.write("not a json file")
    with pytest.raises(ValueError):
        config = load_config(str(config_path))

def test_should_rais_error_if_server_is_in_invalid_format(tmpdir):
    config_data = {
        "port": 16320,
        "servers": [
            {
                "port": 1337
            },
            {
                "host": "127.0.0.1",
                "port": 1338
            }
        ]
    }

    config_path = tmpdir.join("config.json")
    config_path.write(json.dumps(config_data))

    with pytest.raises(ValueError):
        config = load_config(str(config_path))


def test_should_raise_error_if_no_server_list_or_server_list_is_empty(tmpdir):
    config_data = {
        "port": 16320,
    }

    config_path = tmpdir.join("config.json")
    config_path.write(json.dumps(config_data))

    with pytest.raises(ValueError):
        config = load_config(str(config_path))


def test_should_check_if_servers_in_list_are_instances_of_backend_server(config_file):
    config = load_config(config_file)
    for server in config.servers:
        assert isinstance(server, BackendServer)