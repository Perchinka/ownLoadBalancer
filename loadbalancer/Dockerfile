FROM gcc:latest
WORKDIR /app
COPY src/ .
RUN gcc -o loadbalancer loadbalancer.c
CMD ["./loadbalancer"]

