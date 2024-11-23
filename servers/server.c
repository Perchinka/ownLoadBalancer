#include <arpa/inet.h>
#include <bits/pthreadtypes.h>
#include <netinet/in.h>
#include <pthread.h>
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <time.h>
#include <unistd.h>

#define BUF_SIZE 1024

int server_fd;

void handle_signal(int signal) {
  printf("\nSignal %d received. Shutting down server...\n", signal);

  if (server_fd >= 0) {
    close(server_fd);
    printf("Server socket closed.\n");
  }

  exit(0);
}

void *handle_client(void *arg) {
  int client_fd = *(int *)arg;
  free(arg);
  char buffer[BUF_SIZE] = {0};
  int valread;

  while (1) {
    memset(buffer, 0, BUF_SIZE);
    valread = read(client_fd, buffer, BUF_SIZE);

    if (valread == 0) {
      printf("Client disconnected\n");
      break;
    }

    if (valread < 0) {
      perror("Read Error");
      break;
    }
    printf("Recieved: %s\n", buffer);

    const char *http_response = "HTTP/1.1 200 OK\r\n"
                                "Content-Type: text/plain\r\n"
                                "Content-Length: 18\r\n" // Length of the body
                                "\r\n"
                                "Hello from backend";

    if (send(client_fd, http_response, strlen(http_response), 0) < 0) {
      perror("Send Error");
      close(client_fd);
      pthread_exit(NULL);
    }
  }

  send(client_fd, buffer, BUF_SIZE, 0);

  close(client_fd);
  pthread_exit(NULL);
}

void server(int port) {
  struct sockaddr_in address;
  int addrlen = sizeof(address);

  signal(SIGINT, handle_signal);
  signal(SIGTERM, handle_signal);

  if ((server_fd = socket(AF_INET, SOCK_STREAM, 0)) == 0) {
    perror("Socket failed");
    exit(EXIT_FAILURE);
  }

  address.sin_family = AF_INET;
  address.sin_addr.s_addr = INADDR_ANY;
  address.sin_port = htons(port);

  if (bind(server_fd, (struct sockaddr *)&address, sizeof(address)) < 0) {
    perror("Bind failed");
    close(server_fd);
    exit(EXIT_FAILURE);
  }

  if (listen(server_fd, 3) < 0) {
    perror("Listen failed");
    close(server_fd);
    exit(EXIT_FAILURE);
  }

  printf("Server is listening on the port %d\n", port);

  while (1) {
    int *client_fd = malloc(sizeof(int));
    if ((*client_fd = accept(server_fd, (struct sockaddr *)&address,
                             (socklen_t *)&addrlen)) < 0) {
      perror("Accept failed");
      free(client_fd);
      continue;
    }

    pthread_t thread_id;
    if (pthread_create(&thread_id, NULL, handle_client, (void *)client_fd) !=
        0) {
      perror("Failed to create thread");
      close(*client_fd);
      free(client_fd);
    }
  }

  close(server_fd);
}

int main(int argc, char *argv[]) {
  if (argc < 2) {
    fprintf(stderr, "Usage: %s <port>\n", argv[0]);
    exit(EXIT_FAILURE);
  }

  int port = atoi(argv[1]);
  server(port);
}
