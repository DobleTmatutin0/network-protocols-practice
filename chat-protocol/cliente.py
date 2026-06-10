import socket
import sys
import os
import threading

sys.stdout.reconfigure(encoding="utf-8")

BANNER = """

            █████████████████████████████████
            ██ ▄▄▄▄▄ █▀▀ ██▀▀ ▀  ▄▀█ ▄▄▄▄▄ ██
            ██ █   █ █▄▀██▀█▄▀▀▄█▄▄█ █   █ ██
            ██ █▄▄▄█ █ ▄ █ ▀▀ ▀  ▀██ █▄▄▄█ ██
            ██▄▄▄▄▄▄▄█ █ ▀▄█ █▄▀ ▀▄█▄▄▄▄▄▄▄██
            ██  ▀▄▀█▄▄█▀█  ▀ █▀▀▀█▀█ ▄▄▀▄▄▀██
            ███▀ ▄▄▄▄  ▀▀  ▀█▀▄▄▀▄▄█▄▀▀▄  ███
            ██▀ ▀█▄ ▄█▄▀▄ █▄█▀█ █ ▄ ▄▀█▄█▄▄██
            ███▄▄▀ ▀▄ ▀▄▄ █  ▀   ▀ ▄▀██ ▄ ▄██
            ███ ▄ ▄▄▄ ██ █ ▄██▀▄▀▄▄▄▀ █▀█▄▀██
            ██▄█▄█▄▀▄█▀▀▀▄ █▄▀█▀█▀▄▄ ▄███  ██
            ██▄██▄█▄▄█   ▀█ ▄▄█▀█▀ ▄▄▄ █ ▀▀██
            ██ ▄▄▄▄▄ █▄▄ ██▀▄█▀▄ █ █▄█ ▀▀▄▀██
            ██ █   █ █▀ ▀▀ █▀██▄█▀▄▄ ▄ ▀▀▀███
            ██ █▄▄▄█ █▀█▄█ ▀▀█▀ ▄▄▀▄██ ▄▄▀▄██
            ██▄▄▄▄▄▄▄█▄██▄▄▄▄▄▄▄▄█▄██▄▄██▄███
            ▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀

                by el Team mas picantovich
                            
 ██████╗██╗  ██╗ █████╗ ████████╗████████╗███████╗██████╗ 
██╔════╝██║  ██║██╔══██╗╚══██╔══╝╚══██╔══╝██╔════╝██╔══██╗
██║     ███████║███████║   ██║      ██║   █████╗  ██████╔╝
██║     ██╔══██║██╔══██║   ██║      ██║   ██╔══╝  ██╔══██╗
╚██████╗██║  ██║██║  ██║   ██║      ██║   ███████╗██║  ██║
 ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝      ╚═╝   ╚══════╝╚═╝  ╚═╝
        Cliente de chat  ·  IF019 Redes  ·  UNPSJB
"""
print(BANNER)

def mostrar_banner():
    print(BANNER)

def mostrar_ayuda():
    print(
        """
Comandos:
  /banner                  mostrar banner
  /list                    ver quién está conectado
  /msg <destino> <texto>   mandar un mensaje privado
  /broadcast               Enviar mensaje a todos en la red
  /who <nombre>            info de un usuario
  /ping                    chequear la conexión
  /help                    esta ayuda
  /quit                    salir
"""
    )

def manejar_entrada(s, texto):
    texto = texto.strip()
    if not texto:
        return "local"  # ignorar líneas vacías
    if texto == "/banner":
        mostrar_banner()
        return "local"
    
    # --- comandos LOCALES (no van al server) ---
    if texto == "/help":
        mostrar_ayuda()
        return "local"
    if texto == "/quit":
        detener.set()  # así el hilo receptor no lo toma como caída del server
        s.sendall(b"QUIT\n")  # le avisamos al server antes de irnos
        return "salir"

    # --- comandos de RED (se traducen al protocolo y se mandan) ---
    if texto == "/list":
        s.sendall(b"LIST\n")
        return "red"
    elif texto.startswith("/msg "):
        cuerpo = texto[len("/msg ") :]  # "ana hola" -> "MSG ana hola"
        s.sendall(("MSG " + cuerpo + "\n").encode())
        return "red"
    
        # --- comandos de RED (se traducen al protocolo y se mandan) ---
    if texto == "/ping":
        s.sendall(b"PING\n")
        return "red"
    elif texto.startswith("/all "):
        cuerpo = texto[len("/all ") :]
        s.sendall(("ALL " + cuerpo + "\n").encode())
        return "red"
    print("Comando desconocido. Escribí /help para ver la lista.")
    return "local"


# Hilo receptor: lee del socket todo el tiempo, para que los mensajes
# aparezcan apenas llegan y no recién cuando nosotros mandamos algo
detener = threading.Event()

def recibir_mensajes(s):
    while True:
        try:
            datos = s.recv(1024)
        except OSError:
            break  # el hilo principal cerró el socket
        if not datos:
            if detener.is_set():
                break  # cierre normal por /quit
            print("\n[Error] El servidor cerró la conexión")
            os._exit(1)  # input() bloquea el hilo principal, salimos desde acá
        print(f"\r[Chat] {datos.decode().strip()}\n>", end="", flush=True)


# --------------PROGRAMA-------------------------
# Conectar al sv
host = sys.argv[1] if len(sys.argv) > 1 else "138.36.99.9"
port = 8888

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print("[CLIENT] Conectando al servidor")
try:
    s.connect((host, port))
except OSError:
    print("[ERROR] Server inalcanzable, ¿está online?")        
    sys.exit(1) 
print(f"[CLIENT] Conectado al servidor: {host}:{port}")

# Login
nombre = input("Quien sos?: ")
s.sendall(("LOGIN " + nombre + "\n").encode())
print(f"[Login] Login enviado: {nombre} a {host}:{port}")
respuesta = s.recv(1024).decode()
print(f"[Login] Respuesta del servidor: {respuesta}")
if respuesta.startswith("OK"):
    print(f"[Login] entraste al chat: {nombre}", respuesta)
    s.sendall(("LIST\n").encode())
    respuesta = s.recv(1024).decode()
    print(f"[CLIENT] Respuesta del servidor: {respuesta}")
else:
    print("[Error] Error en el login", respuesta)
    s.close()
    sys.exit()

# A partir de acá el socket lo lee solo el hilo receptor
hilo_receptor = threading.Thread(target=recibir_mensajes, args=(s,), daemon=True)
hilo_receptor.start()

# Loop: este hilo solo lee teclado y manda
while True:
    texto = input(">")
    estado = manejar_entrada(s, texto)

    if estado == "salir":
        break


# Cerrar la conexión
detener.set()
s.close()
print("[CLIENT] Conexión cerrada")
