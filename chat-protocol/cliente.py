import socket
import sys
import threading
import os

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
  /help                    esta ayuda
  /quit                    salir
"""
    )


def enviar_archivo(s, dest, ruta):
    """
    Envvia un archivo al server.
    El archivo debe existir en la ruta dada.
    """
    try:
        with open(ruta, "rb") as f:
            datos = f.read()
    except FileNotFoundError:
        print(f"\n[!] El archivo {ruta} no existe")
        return

    nombre = os.path.basename(ruta)
    tam = len(datos)

    header = f"FILE {dest} {nombre} {tam}\n"
    s.sendall(header.encode())

    s.sendall(datos)
    print(f"[file] Enviado {nombre} ({tam} bytes) a {dest}")


def recibir(s):
    """
    Corre en un hilo aparte. Lee el socket todo el tiempo y muestra lo que llega,
    sea una respuesta del server o un mensaje de otro usuario.
    """
    buffer = ""
    while True:
        try:
            data = s.recv(1024)
        except OSError:
            break
        if not data:
            print("\n[!] El server cerro la conexion")
            break
        buffer += data.decode()
        # Procesar de a lineas completas (con "\n")
        while "\n" in buffer:
            linea, buffer = buffer.split("\n", 1)
            procesar_mensaje(linea.strip())


def procesar_mensaje(linea):
    """
    Procesa un mensaje del server.
    Si es un mensaje de otro usuario, lo muestra.
    Si es una respuesta OK o ERROR, lo muestra.
    """
    if not linea:
        return
    if linea.startswith("MSG "):
        resto = linea[len("MSG ") :]
        origen, _, texto = resto.partition(" ")
        print(f"\n{origen}: {texto}")
    elif linea.startswith("OK"):
        print(f"\n[ok] {linea}")
    elif linea.startswith("ERROR"):
        print(f"\n[error] {linea}")
    # TODO: FILE <origen> <nombre> <tam> ...   -> recibir archivo (lo vemos aparte)
    else:
        print(f"\n{linea}")


def manejar_entrada(s, texto):
    """
    Maneja la entrada del usuario.
    Si es local (comando de cliente), la ejecuta.
    Si es red (comando de red), la envía al server.
    Si es salir, cierra la conexión.
    """

    texto = texto.strip()
    if not texto:
        return "local"  # ignorar líneas vacías

    # --- comandos LOCALES (no van al server) ---
    if texto == "/banner":
        mostrar_banner()
        return "local"
    if texto == "/help":
        mostrar_ayuda()
        return "local"
    if texto == "/quit":
        s.sendall(b"LOGOUT\n")
        return "salir"

    # --- comandos de RED (se traducen al protocolo y se mandan) ---
    if texto == "/list":
        s.sendall(b"LIST\n")
        return "red"
    elif texto.startswith("/msg "):
        cuerpo = texto[len("/msg ") :]
        s.sendall(("MSG " + cuerpo + "\n").encode())
        return "red"
    elif texto.startswith("/file "):
        cuerpo = texto[len("/file ") :]
        print(f"[DEBUG] /file {cuerpo}")
        partes = cuerpo.split(" ", 1)
        if len(partes) < 2:
            print("Comando inválido, uso: /file <destino> <ruta>")
            return "local"
        dest, ruta = partes
        print(f"[DEBUG] Enviando {ruta} a {dest}")
        enviar_archivo(s, dest, ruta)
        return "red"
    print("Comando desconocido. Escribí /help para ver la lista.")
    return "local"


# --------------PROGRAMA-------------------------
# Conectar al server
host = "127.0.0.1"
port = 8888

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print("[CLIENT] Conectando al servidor")
s.connect((host, port))
print(f"[CLIENT] Conectado al servidor: {host}:{port}")

# Login (handshake SINCRONO, antes de arrancar el hilo)
nombre = input("Quien sos?: ")
s.sendall(("LOGIN " + nombre + "\n").encode())
print(f"[Login] Login enviado: {nombre}")
respuesta = s.recv(1024).decode()
print(f"[Login] Respuesta del servidor: {respuesta.strip()}")
if respuesta.startswith("OK"):
    print(f"[Login] Entraste al chat como: {nombre}")
else:
    print("[Error] Error en el login:", respuesta.strip())
    s.close()
    sys.exit()

# Arrancar el hilo receptor
hilo = threading.Thread(target=recibir, args=(s,), daemon=True)
hilo.start()

# Loop principal: solo lee el teclado y manda. NO hace recv (de eso se encarga el hilo)
while True:
    texto = input("> ")
    estado = manejar_entrada(s, texto)
    if estado == "salir":
        break

# Cerrar la conexion
s.close()
print("[CLIENT] Conexión cerrada")
