FROM gcc:latest
WORKDIR /app
COPY src/ .
RUN gcc -o loadbalancer main.c
CMD ["./loadbalancer"]

