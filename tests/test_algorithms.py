import pytest
from ownloadbalancer.algorithms.algorithms import choose, algorithms
from ownloadbalancer.backend_server import BackendServer

@pytest.fixture
def server_list():
    return [BackendServer("127.0.0.1", 1337), BackendServer("127.0.0.1", 1338), BackendServer("127.0.0.1", 1339)]

def test_choose_should_return_a_random_server_if_random_algorithm(server_list):
    server = choose(server_list, algorithms["RANDOM"]())
    assert server in server_list

def test_choose_should_return_a_server_with_least_connections_if_least_connection_algorithm(server_list):
    server = choose(server_list, algorithms["LEAST_CONNECTION"]())
    for s in server_list:
        assert server.connections <= s.connections

def test_choose_should_return_a_server_in_round_robin_if_round_robin_algorithm(server_list):
    algo = algorithms["ROUND_ROBIN"]()
    for i in range(0, 13):
        server = choose(server_list, algo)
        assert server == server_list[i % len(server_list)]
