
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
#define IP "0.0.0.0"
#define MAX_CLIENTS 10
#define MAX_USERNAME 32
#define BUFFER_SIZE 1025



Client clients[MAX_CLIENTS];

int max_sd, sd, activity, i, valread;

// Socket File Descriptor
static int socketFileDescriptor;

fd_set fds_to_select;

struct sockaddr_in client_addr;

void signHandler(int signal) {
    close(socketFileDescriptor);
    exit(EXIT_SUCCESS);
}


// Buscar un cliente por su socket (id)
Client* find_client_by_socket(int socket) {
    for (int i = 0; i < MAX_CLIENTS; i++) {
        if (clients[i].socket_fd == socket) {
            return &clients[i];
        }
    }
    return NULL;
}

// Buscar un cliente por su username
Client* find_client_by_username(const char* username) {
    for (int i = 0; i < MAX_CLIENTS; i++) {
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

    /* Permitir reutilizar la dirección/puerto inmediatamente después de cerrar */
    int opt = 1;
    if (setsockopt(socketFileDescriptor, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt)) < 0) {
        perror("setsockopt() falló");
        close(socketFileDescriptor);
        exit(EXIT_FAILURE);
    }

    /* Registrar handler para Ctrl+C que cierre el socket correctamente */
    signal(SIGINT, signHandler);

    memset(&server_addr, 0, sizeof(server_addr));
    server_addr.sin_family = AF_INET;

    if (argc == 3) {
        // use argument IP and PORT
        server_addr.sin_addr.s_addr = inet_addr(argv[1]);
        server_addr.sin_port = htons((uint16_t) atoi(argv[2]));
    }
    else {
        // use default IP and PORT
        server_addr.sin_addr.s_addr = inet_addr(IP);
        server_addr.sin_port = htons(PORT);
    }

    if (bind(socketFileDescriptor, (struct sockaddr*)&server_addr, sizeof(server_addr)) < 0) {
        perror("bind() falló");
        exit(EXIT_FAILURE);
    }

    printf("Server corriendo exitosamente\n");

    if (listen(socketFileDescriptor, MAX_CLIENTS) < 0) {
        perror("listen() falló");
        exit(EXIT_FAILURE);
    }

    // inicializa todos los sockets en 0, es decir q estan inactivos
    for (int i = 0; i < MAX_CLIENTS ;i ++) {
        clients[i].socket_fd = 0;
    }

    while (1) {
        // limpiar conjunto de descriptores q escucha el sv
        FD_ZERO(&fds_to_select);

        FD_SET(socketFileDescriptor, &fds_to_select);
        max_sd = socketFileDescriptor;

         // Agregar los sockets de los clientes al conjunto
        for (i = 0; i < MAX_CLIENTS; i++) {
            sd = clients[i].socket_fd;
            if (sd > 0) {
                FD_SET(sd, &fds_to_select);
            }
            // Actualizar el descriptor máximo para select
            if (sd > max_sd) {
                max_sd = sd;
            }
        }

        activity = select(max_sd + 1, &fds_to_select, NULL, NULL, NULL);

        if (FD_ISSET(socketFileDescriptor, &fds_to_select)) {
            socklen_t client_len = sizeof(client_addr);

            int new_socket = accept(socketFileDescriptor, (struct sockaddr *)&client_addr, &client_len);
            if (new_socket < 0) {
                perror("accept");
                exit(EXIT_FAILURE);
            }
            printf("Nueva conexión, socket fd: %d, IP: %s, Puerto: %d\n", 
                   new_socket, inet_ntoa(client_addr.sin_addr), ntohs(client_addr.sin_port));

            // Guardar nuevo socket en el array
            for (i = 0; i < MAX_CLIENTS; i++) {
                if (clients[i].socket_fd == 0) {
                    clients[i].socket_fd = new_socket;
                    clients[i].logged_in = false;
                    clients[i].username[0] = '\0';
                    break;
                }
            }
        }

        for (i = 0; i < MAX_CLIENTS; i++) {
            sd = clients[i].socket_fd;

            if (sd > 0 && FD_ISSET(sd, &fds_to_select)) {
                char buffer[BUFFER_SIZE];
                int bytes = recv(sd, buffer, sizeof(buffer) - 1, 0);

                if (bytes == 0) {
                    printf("Cliente %d desconectado\n", sd);
                    close(sd);
                    clients[i].socket_fd = 0;
                    clients[i].logged_in = false;
                    clients[i].username[0] = '\0';
                    continue;
                }

                if (bytes < 0) {
                    perror("recv");
                    continue;
                }

                buffer[bytes] = '\0';
                printf("Cliente %d envió %d bytes: %s\n", sd, bytes, buffer);

                // checkeq q el cliente este loggeado o intentando loggearse
                if (!clients[i].logged_in &&
                    strncmp(buffer, "LOGIN ", 6) != 0) {
                    
                    send_to_client(
                        sd,
                        "ERROR Debe hacer LOGIN primero\n"
                    );
                
                    continue;
                }

                if (strncmp(buffer, "LOGIN ", 6) == 0) {
                    char nombre[MAX_USERNAME];
                    if (sscanf(buffer + 6, "%31s", nombre) == 1) {
                        strncpy(clients[i].username, nombre, MAX_USERNAME - 1);
                        clients[i].username[MAX_USERNAME - 1] = '\0';
                        clients[i].logged_in = true;
                        send_to_client(sd, "OK\n");
                    } else {
                        send_to_client(sd, "ERROR LOGIN Nombre inválido\n");
                    }
                } else if (strncmp(buffer, "LIST", 4) == 0) {
                    char lista[BUFFER_SIZE];
                    lista[0] = '\0';
                    for (int j = 0; j < MAX_CLIENTS; j++) {
                        if (clients[j].socket_fd != 0 && clients[j].logged_in) {
                            if (lista[0] != '\0') {
                                strncat(lista, ",", sizeof(lista) - strlen(lista) - 1);
                            }
                            strncat(lista, clients[j].username, sizeof(lista) - strlen(lista) - 1);
                        }
                    }
                    char respuesta[BUFFER_SIZE];
                    snprintf(respuesta, sizeof(respuesta), "Usuarios conectados: %s\n", lista);
                    send_to_client(sd, respuesta);
                } else if (strncmp(buffer, "MSG ", 4) == 0) {
                    char destino[MAX_USERNAME];
                    char mensaje[BUFFER_SIZE];

                    if (sscanf(buffer + 4, "%31s %[^\n]", destino, mensaje) == 2) {
                    
                        Client* receptor = find_client_by_username(destino);
                    
                        if (receptor == NULL) {
                            send_to_client(sd, "ERROR Usuario no encontrado\n");
                        } else {
                        
                            char salida[BUFFER_SIZE];
                        
                            snprintf(
                                salida,
                                sizeof(salida),
                                "MSG %s %s\n",
                                clients[i].username,
                                mensaje
                            );
                        
                            send_to_client(
                                receptor->socket_fd,
                                salida
                            );
                        
                            send_to_client(
                                sd,
                                "OK MSG\n"
                            );
                        }
                    } else {
                        send_to_client(
                            sd,
                            "ERROR Formato: MSG <destino> <mensaje>\n"
                        );
                    }
                
                } else if (strncmp(buffer, "QUIT", 4) == 0) {

                    send_to_client(sd, "OK QUIT\n");
                    close(sd);
                    clients[i].socket_fd = 0;
                    clients[i].logged_in = false;
                    clients[i].username[0] = '\0';
                } else if (strncmp(buffer, "PING", 4) == 0) {
                    send_to_client(sd, "PONG");
                } else if (strncmp(buffer, "ALL ", 4) == 0) {
                    char mensaje[BUFFER_SIZE];
                    snprintf(mensaje, sizeof(mensaje), "MSG %s %s\n",
                            clients[i].username, buffer + 4);

                    for (int j = 0; j < MAX_CLIENTS; j++) {
                        if (clients[j].socket_fd != 0 &&
                            clients[j].logged_in &&
                            clients[j].socket_fd != sd) {
                            send_to_client(clients[j].socket_fd, mensaje);
                        }
                    }

                    send_to_client(sd, "OK ALL\n");
                } else {
                    send_to_client(sd, "ERROR Comando desconocido\n");
                }
            }
        }

    }
    
}