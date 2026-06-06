#include <stdbool.h>

#define MAX_USERNAME 32


typedef struct {
    int socket_fd;                     
    char username[MAX_USERNAME];    
    bool logged_in; // Si está logueado es 1, sino 0
} Client;