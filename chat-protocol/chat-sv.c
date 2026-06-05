
// Librerias del estandar ANSI / ISO C
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <signal.h>

// Librerias del estandar POSIX
#include <sys/socket.h> // Berkeley sockets
#include <arpa/inet.h> // functions for manipulate ip addresses (part of Berkeley sockets)
#include <netinet/ip.h> // defines InternetProtocol and addess family (part of Berkeley sockets)
#include <unistd.h> // syscalls
#include <sys/types.h> // defines various data types

// Direccion por defecto del servidor.
#define PORT 8888;
#define IP "127.0.0.1";

// Socket File Descriptor
static int socketFileDescriptor;

// Close the soket when a "insert signal" arrives.
void signHandler(int signal) {
    close(socketFileDescriptor);
    exit(EXIT_SUCCESS);
}

int main(int argc, char* argv[]) {
    struct sockaddr_in server_addr;

    socketFileDescriptor = socket(AF_INET, SOCK_DGRAM, IPPROTO_TCP); // si no funciona IPPROTO_TCP cambiar por 0
}