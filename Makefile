CC = gcc
CFLAGS = -Wall -Wextra -g
LDFLAGS = 

SRC = $(wildcard src/*.c)
OBJ = $(SRC:.c=.o)

TARGET = bin/loadbalancer

all: $(TARGET)

$(TARGET): $(OBJ)
	@mkdir -p bin
	$(CC) $(CFLAGS) -o $@ $^ $(LDFLAGS)

clean:
	rm -rf bin src/*.o

run: clean $(TARGET)
	./$(TARGET)

test: 
	$(CC) $(CFLAGS) -o bin/test tests/test_loadbalancer.c src/loadbalancer.c src/utils.c
	./bin/test

