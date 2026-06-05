
// Librerias del estandar ANSI / ISO C
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <signal.h>
#include <sys/socket.h>
#include <arpa/inet.h>
#include <netinet/ip.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/select.h>
#include "client.h"
#define PORT 8888
#define IP "127.0.0.1"
#define MAX_CLIENTS 10
#define BUFFER_SIZE 1024
#define MAX_USERNAME 50



Client clients[MAX_CLIENTS];
int num_clients = 0;  // Cuántos clientes hay conectados ahora

// Socket File Descriptor
static int socketFileDescriptor;

void signHandler(int signal) {
    close(socketFileDescriptor);
    exit(EXIT_SUCCESS);
}


// Buscar un cliente por su socket (id)
Client* find_client_by_socket(int socket) {
    for (int i = 0; i < num_clients; i++) {
        if (clients[i].socket == socket) {
            return &clients[i];
        }
    }
    return NULL;
}

// Buscar un cliente por su username
Client* find_client_by_username(const char* username) {
    for (int i = 0; i < num_clients; i++) {
        if (clients[i].logged_in && strcmp(clients[i].username, username) == 0) {
            return &clients[i];
        }
    }
    return NULL;
}

// Enviar un mensaje a un cliente específico
void send_to_client(int socket, const char* message) {
    send(socket, message, strlen(message), 0);
}

int main(int argc, char* argv[]) {
    struct sockaddr_in server_addr;
    
    printf("[SERVIDOR] Iniciando Chat Server...\n");
    
    // ========== CREAR SOCKET SERVIDOR ==========
    socketFileDescriptor = socket(AF_INET, SOCK_DGRAM, 0);

    
    if (socketFileDescriptor < 0) {
        perror("socket() falló");
        exit(EXIT_FAILURE);
    }
    printf("[SERVIDOR] Socket creado exitosamente\n");
}