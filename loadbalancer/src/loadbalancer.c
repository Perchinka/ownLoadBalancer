#include <arpa/inet.h>
#include <bits/pthreadtypes.h>
#include <netdb.h>
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
#define PORT 7070
#define MAX_BACKENDS 10

int server_fd;
int backend_fds[MAX_BACKENDS];
int num_backends = 0;

void handle_signal(int signal) {
  printf("\nSignal %d received. Shutting down server...\n", signal);

  if (server_fd >= 0) {
    close(server_fd);
    printf("Server socket closed.\n");
    fflush(stdout);
  }

  exit(0);
}

int choose_server() {
  static int index = 0;
  if (num_backends == 0) {
    fprintf(stderr, "No backends available.\n");
    fflush(stderr);
    return -1;
  }
  int fd = backend_fds[index];
  index = (index + 1) % num_backends;
  return fd;
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
      // printf("Client disconnected\n");
      // fflush(stdout);
      break;
    }

    if (valread < 0) {
      perror("Read Error");
      fflush(stderr);
      break;
    }

    int backend_fd = choose_server();
    if (backend_fd < 0) {
      printf("No available backend server.\n");
      fflush(stdout);
      break;
    }

    send(backend_fd, buffer, valread, 0);
    valread = read(backend_fd, buffer, BUF_SIZE);
    send(client_fd, buffer, valread, 0);
  }

  close(client_fd);
  pthread_exit(NULL);
}

void loadbalancer() {
  struct sockaddr_in address;
  int addrlen = sizeof(address);

  signal(SIGINT, handle_signal);
  signal(SIGTERM, handle_signal);

  if ((server_fd = socket(AF_INET, SOCK_STREAM, 0)) == 0) {
    perror("Socket failed");
    fflush(stderr);
    exit(EXIT_FAILURE);
  }

  address.sin_family = AF_INET;
  address.sin_addr.s_addr = INADDR_ANY;
  address.sin_port = htons(PORT);

  if (bind(server_fd, (struct sockaddr *)&address, sizeof(address)) < 0) {
    perror("Bind failed");
    fflush(stderr);
    close(server_fd);
    exit(EXIT_FAILURE);
  }

  if (listen(server_fd, 3) < 0) {
    perror("Listen failed");
    fflush(stderr);
    close(server_fd);
    exit(EXIT_FAILURE);
  }

  printf("Loadbalancer is listening on the port %d\n", PORT);
  fflush(stdout);

  while (1) {
    int *client_fd = malloc(sizeof(int));
    if ((*client_fd = accept(server_fd, (struct sockaddr *)&address,
                             (socklen_t *)&addrlen)) < 0) {
      perror("Accept failed");
      fflush(stderr);
      free(client_fd);
      continue;
    }

    pthread_t thread_id;
    if (pthread_create(&thread_id, NULL, handle_client, (void *)client_fd) !=
        0) {
      perror("Failed to create thread");
      fflush(stderr);
      close(*client_fd);
      free(client_fd);
    }
  }

  close(server_fd);
}

int establish_socket(const char *host, int port) {
  int sock_fd = socket(AF_INET, SOCK_STREAM, 0);
  if (sock_fd < 0) {
    perror("Socket creation failed");
    fflush(stderr);
    return -1;
  }

  struct addrinfo hints, *res;
  memset(&hints, 0, sizeof(hints));
  hints.ai_family = AF_INET;
  hints.ai_socktype = SOCK_STREAM;

  char port_str[6];
  snprintf(port_str, sizeof(port_str), "%d", port);

  if (getaddrinfo(host, port_str, &hints, &res) != 0) {
    fprintf(stderr, "Failed to resolve host: %s\n", host);
    fflush(stderr);
    close(sock_fd);
    return -1;
  }

  if (connect(sock_fd, res->ai_addr, res->ai_addrlen) < 0) {
    perror("Connection failed");
    fflush(stderr);
    close(sock_fd);
    return -1;
  }

  printf("Connected to server %s:%d\n", host, port);
  fflush(stdout);
  return sock_fd;
}

void connect_to_backend(const char *host_port_list) {
  char *list_copy = strdup(host_port_list);
  if (!list_copy) {
    perror("Failed to allocate memory for host list copy");
    fflush(stderr);
    exit(EXIT_FAILURE);
  }

  char *token = strtok(list_copy, ",");
  while (token && num_backends < MAX_BACKENDS) {
    char *colon = strchr(token, ':');
    if (!colon) {
      fprintf(stderr, "Invalid backend format: %s\n", token);
      fflush(stderr);
      token = strtok(NULL, ",");
      continue;
    }

    *colon = '\0';
    const char *host = token;
    int port = atoi(colon + 1);

    int backend_fd = establish_socket(host, port);
    if (backend_fd >= 0) {
      backend_fds[num_backends++] = backend_fd;
    }

    token = strtok(NULL, ",");
  }

  free(list_copy);

  if (num_backends == 0) {
    fprintf(stderr, "No valid backends were connected. Exiting.\n");
    fflush(stderr);
    exit(EXIT_FAILURE);
  }

  printf("Successfully connected to %d backend(s).\n", num_backends);
}

int main(int argc, char *argv[]) {
  const char *backend_env = getenv("BACKEND_SERVERS");
  if (!backend_env) {
    fprintf(stderr, "Environment variable BACKEND_SERVERS is not set.\n");
    fflush(stderr);
    return EXIT_FAILURE;
  }

  connect_to_backend(backend_env);

  loadbalancer();

  return 0;
}
