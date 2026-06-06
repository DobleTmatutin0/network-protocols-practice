#include <stdint.h>

typedef enum {
    LOG_IN = 1,
    LOG_OUT = 2,
    LIST_USER = 3,
    SEND_MESSAGE = 4,
    SEND_FILE = 5,
    LOG_IN_OK = 6,
    LOG_IN_REJECTED = 7,
    USER_LIST = 8,
    ACK = 9,
    UNACK = 10,
    ERROR = 11
} Opcode;

typedef struct {
    Opcode opcode;
    uint16_t length;
    char to[32];
    char data[512];
} Packet;