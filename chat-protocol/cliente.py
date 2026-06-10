import socket
import sys

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
    elif texto.startwith("/all"):
        cuerpo = texto[len("/all ") :]
        s.sendall(("ALL " + cuerpo + "\n").encode())
        return "red"
    elif texto.startwhit("/ping"):
        cuerpo = texto[len("/ping ") :]
        s.sendall(("PING""\n").encode())
        return "red"
    print("Comando desconocido. Escribí /help para ver la lista.")
    return "local"


# --------------PROGRAMA-------------------------
# Conectar al sv
host = "127.0.0.1"
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

# Loop
while True:
    texto = input(">")
    estado = manejar_entrada(s, texto)

    if estado == "salir":
        break

    if estado == "red":
        respuesta = s.recv(1024).decode()
        if not respuesta:
            print("[Error] Error de conexion")
            break
        print(f"[Chat] Recibido: {respuesta}")


# Cerrar la conexión
s.close()
print("[CLIENT] Conexión cerrada")
