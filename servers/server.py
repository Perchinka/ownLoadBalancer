import socket
import threading
import argparse
import signal
import sys

server_socket = None


def handle_client(client_socket):
    try:
        request = client_socket.recv(1024).decode("utf-8")
        print(f"Received request:\n{request}")

        http_response = (
            "HTTP/1.1 200 OK\r\n"
            "Content-Type: text/plain\r\n"
            "Content-Length: 18\r\n"
            "\r\n"
            "Hello from backend"
        )

        client_socket.sendall(http_response.encode("utf-8"))
        print("HTTP 200 Response sent to client")
    except Exception as e:
        print(f"Error while handling client: {e}")
    finally:
        client_socket.close()


def start_server(host, port):
    global server_socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)
    print(f"Server started on {host}:{port}")

    try:
        while True:
            client_socket, addr = server_socket.accept()
            print(f"Connection received from {addr}")
            client_handler = threading.Thread(
                target=handle_client, args=(client_socket,)
            )
            client_handler.start()
    except KeyboardInterrupt:
        print("\nServer interrupted by user")
    finally:
        if server_socket:
            server_socket.close()
            print("Server socket closed. Unbinding complete.")


def signal_handler(sig, frame):
    global server_socket
    print("\nSignal received, shutting down the server...")
    if server_socket:
        server_socket.close()
    sys.exit(0)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Simple HTTP Server")
    parser.add_argument(
        "--host",
        type=str,
        default="0.0.0.0",
        help="Host to bind the server to (default: 0.0.0.0)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8080,
        help="Port to bind the server to (default: 8080)",
    )
    args = parser.parse_args()
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    start_server(args.host, args.port)
