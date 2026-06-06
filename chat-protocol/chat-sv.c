
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
    
    socketFileDescriptor = socket(AF_INET, SOCK_STREAM, 0);
    if (socketFileDescriptor < 0) {
        perror("socket() falló");
        exit(EXIT_FAILURE);
    }

    memset(&server_addr, 0, sizeof(server_addr));
    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(PORT);
    server_addr.sin_addr.s_addr = inet_addr(IP);

    if (bind(socketFileDescriptor, (struct sockaddr*)&server_addr, sizeof(server_addr)) < 0) {
        perror("bind() falló");
        exit(EXIT_FAILURE);
    }

    printf("Server corriendo exitosamente\n");

    if (listen(socketFileDescriptor, MAX_CLIENTS) < 0) {
        perror("listen() falló");
        exit(EXIT_FAILURE);
    }

    while (1) {
        struct sockaddr_in client_addr;
        socklen_t client_len = sizeof(client_addr);
        int client_socket = accept(socketFileDescriptor, (struct sockaddr*)&client_addr, &client_len);

        if (client_socket < 0) {
            perror("accept() falló");
            continue;
        }

        int added = 0;
        for (int i = 0; i < MAX_CLIENTS; i++) {
            if (clients[i].socket == 0) {
                clients[i].socket = client_socket;
                clients[i].logged_in = 0;
                clients[i].username[0] = '\0';
                printf("[SERVIDOR] Cliente nuevo aceptado en slot %d\n", i);
                added = 1;
                break;
            }
        }

        if (!added) {
            send_to_client(client_socket, "ERROR Servidor lleno\n");
            close(client_socket);
            printf("[SERVIDOR] Rechazado cliente: servidor lleno\n");
        }
    }
    



}