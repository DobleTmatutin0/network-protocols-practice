#socket.socket(socket.AF_INET, socket.SOCK_STREAM) → crea un socket TCP 
# (igual que en C: AF_INET = IPv4, SOCK_STREAM = TCP).

#s.connect((host, port)) → se conecta al servidor. 
# Ojo que el argumento es una tupla (host, port), con doble paréntesis.

#s.sendall(datos) → manda datos (en bytes). 
# Se usa sendall y no send porque send puede mandar solo una parte; sendall se asegura de mandar todo.

#s.recv(1024) → recibe hasta 1024 bytes y los devuelve como bytes. 
# Si te devuelve b'' (vacío) significa que el server cerró la conexión

#s.close() → cierra el socket

#"hola".encode() y datos.decode() → para pasar de string a bytes y al revés.


host = "127.0.0.1"
port = 8888

create_socket() 
connect(HOST, PORT)

#Bucle de repetir escuchar la lectura de teclado
while True:
    DATA = input("Ingrese algo: " + "\n")
    if DATA == "exit":
        break
    DATA = DATA.encode()
    sendall(DATA)
    recv = recv(1024)
    if not recv:
        break
    print(recv.decode())

close()
