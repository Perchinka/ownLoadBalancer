import pytest
from ownloadbalancer.listener import Listener

def test_listener_should_raise_error_if_no_config_file():
    with pytest.raises(FileNotFoundError):
        listener = Listener(config_file="nonexistent_config.json")



    