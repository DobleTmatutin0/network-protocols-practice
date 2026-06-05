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

# ESTO ES LA CAPA DE TRANSPORTES

import socket

host = "127.0.0.1"
port = 8888

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print("Conectando al servidor")
s.connect((host, port))
print(f"Conectado en {host}:{port}")

print("Conectado al servidor")
# Bucle de repetir escuchar la lectura de teclado
while True:
    DATA = input("Ingrese algo: ")
    print(f"Enviando: {DATA}")
    if DATA == "exit":
        break
    DATA = (DATA + "\n").encode()
    s.sendall(DATA)
    data = s.recv(1024)
    if not data:
        break
    print(f"Recibido: {data.decode()}")

s.close()
print("Conexión cerrada")

# --- Identificación ---
# pedir el nombre al usuario              
nombre = input("Tu nombre: ")

# armar el mensaje segun el protocolo:    
mensaje = "LOGIN " + nombre + "\n"
# enviarlo                                 
s.sendall(mensaje.encode())

# recibir la respuesta del server, ver como armamos el protocolo 
data = s.recv(1024).decode()
print(data)
# interpretarla:
#     si empieza con "OK"    -> mostrar que entraste (con el id si lo devuelve)
#     si empieza con "ERROR" -> mostrar el error y decidir (reintentar o salir)