#define MAX_USERNAME 50

typedef struct {
    int socket;                     
    char username[MAX_USERNAME];    
    int logged_in;                  // Si está logueado es 1, sino 0
} Client;