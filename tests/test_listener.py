import pytest
import asyncio
from ownloadbalancer.listener import Listener
import json

@pytest.fixture
def dummy_client():
    return asyncio.open_connection(host="127.0.0.1", port=16322)

def test_listener_should_raise_error_if_no_config_file():
    with pytest.raises(FileNotFoundError):
        listener = Listener(config_file="nonexistent_config.json")


    