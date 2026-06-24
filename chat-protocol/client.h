#ifndef CLIENT_H
#define CLIENT_H

#include <stdbool.h>

#define MAX_USERNAME 32

typedef enum {
    STATE_NORMAL,
    STATE_RECEIVING_FILE
} ClientState;

typedef struct {
    int    socket_fd;
    char   username[MAX_USERNAME];
    bool   logged_in;

    ClientState state;
    int    file_remaining;
    int    file_dest_fd;
} Client;

#endif