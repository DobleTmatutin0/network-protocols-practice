import socket
import sys
import os
import threading

sys.stdout.reconfigure(encoding="utf-8")

CHUNK = 1024
ok_file = threading.Event()

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
  /banner                  Mostrar banner
  /list                    Ver quién está conectado
  /msg <destino> <texto>   Mandar un mensaje privado
  /all                     Enviar mensaje a todos en la red
  /file <destino> <ruta>   Enviar un archivo
  /ping                    Chequear la conexión
  /help                    Muestra todos los comandos disponibles
  /quit                    Salir
"""
    )


def enviar_archivo(s, destino, ruta):
    if not os.path.isfile(ruta):
        print(f"Error: El archivo {ruta} no existe")
        return
    tam = os.path.getsize(ruta)
    nombre = os.path.basename(ruta).replace(" ", "_")
    ok_file.clear()
    s.sendall((f"FILE {destino} {nombre} {tam}\n").encode())
    # El server manda OK FILE para confirmar que puede
    if not ok_file.wait(timeout=5):
        print("[File] El servidor no confirmó la transferencia. Envío cancelado.")
        return

    # enviar bytes
    enviados = 0
    with open(ruta, "rb") as f:
        while True:
            datos = f.read(CHUNK)
            if not datos:
                break
            s.sendall(datos)
            enviados += len(datos)

    print(f"[File] Enviado: {nombre} ({enviados} bytes) -> {destino}")


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
    if texto.startswith("/all "):
        cuerpo = texto[len("/all ") :]
        s.sendall(("ALL " + cuerpo + "\n").encode())
        return "red"
    if texto.startswith("/file "):
        partes = texto.split(" ", 2)
        if len(partes) < 3:
            print("[File] Uso: /file <destino> <ruta>")
            return "local"
        enviar_archivo(s, partes[1], partes[2])
        return "red"
    print("Comando desconocido. Escribí /help para ver la lista.")
    return "local"


# Hilo receptor: lee del socket todo el tiempo, para que los mensajes
# aparezcan apenas llegan y no recién cuando nosotros mandamos algo
detener = threading.Event()


def recibir_exactos(s, buffer, cantidad):
    """
    Recibe exactamente cantidad de bytes del socket s en el buffer buffer
    Devuelve (datos, resto_del_buffer)
    """
    while len(buffer) < cantidad:
        datos = s.recv(CHUNK)
        if not datos:
            raise ConnectionError("El servidor cerró la conexión")
        buffer += datos
    return buffer[:cantidad], buffer[cantidad:]


# Buffer compartido para el input parcial y su candado (nivel módulo)
current_input = ""
input_lock = threading.Lock()

try:
    import msvcrt

    def getch():
        return msvcrt.getwch()
except Exception:
    import tty
    import termios

    def getch():
        fd = sys.stdin.fileno()
        old = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old)
        return ch


def read_input(prompt):
    """Lee la línea carácter a carácter manteniendo el buffer parcial en `current_input`.
    Esto permite que el hilo receptor pueda reimprimir lo que el usuario está escribiendo.
    """
    global current_input
    sys.stdout.write(prompt)
    sys.stdout.flush()
    buf = ""
    while True:
        ch = getch()
        # Normalizar retorno de carro/line feed
        if ch in ("\r", "\n"):
            print("")
            with input_lock:
                current_input = ""
            return buf
        # Backspace (Windows/Unix)
        if ch in ("\x08", "\x7f"):
            if len(buf) > 0:
                buf = buf[:-1]
                # borrar caracter en pantalla
                sys.stdout.write('\b \b')
                sys.stdout.flush()
                with input_lock:
                    current_input = buf
            continue
        # Caracter normal: añadir y eco
        buf += ch
        sys.stdout.write(ch)
        sys.stdout.flush()
        with input_lock:
            current_input = buf


def procesar_linea(texto):
    texto = texto.strip()
    if not texto:
        return

    if texto.startswith("MSG "):
        partes = texto.split(" ", 2)
        if len(partes) >= 3:
            remitente, mensaje = partes[1], partes[2]
            # Limpiar línea actual, mostrar mensaje, y reimprimir prompt + texto parcial
            with input_lock:
                cur = current_input
            print(f"\r\033[K{remitente}: {mensaje}")
            sys.stdout.write(">" + cur)
            sys.stdout.flush()
            return

    if texto == "OK FILE":
        ok_file.set()  # despierta a enviar_archivo() que está esperando
        return

    if texto == "OK MSG" or texto == "OK ALL":
        return

    # Limpiar línea actual antes de mostrar respuesta del servidor y reimprimir input parcial
    with input_lock:
        cur = current_input
    print(f"\r\033[K{texto}")
    sys.stdout.write(">" + cur)
    sys.stdout.flush()


def recibir_mensajes(s):
    buffer = b""
    while True:
        try:
            datos = s.recv(CHUNK)
        except OSError:
            break  # el hilo principal cerró el socket
        if not datos:
            if detener.is_set():
                break  # cierre normal por /quit
            print("\n[Error] El servidor cerró la conexión")
            os._exit(1)  # input() bloquea el hilo principal, salimos desde acá

        buffer += datos
        while b"\n" in buffer:
            linea, buffer = buffer.split(b"\n", 1)

            try:
                linea = linea.decode()
            except UnicodeDecodeError:
                print(r"[Error] Error al decodificar línea: {linea}")
                continue

            if linea.startswith("FILE"):
                partes = linea.split(" ")
                if len(partes) != 4 or not partes[3].isdigit():
                    print(rf"[Error] Header invalido {linea}")
                    continue
                remitente, nombre, tam = partes[1], partes[2], int(partes[3])
                # Mostrar cabecera de transferencia sin borrar lo que el usuario está escribiendo
                with input_lock:
                    cur = current_input
                print(rf"[File] {remitente} mandando {nombre} ({tam} bytes)")
                sys.stdout.write(">" + cur)
                sys.stdout.flush()

                try:
                    datos_archivo, buffer = recibir_exactos(s, buffer, tam)
                except ConnectionError as e:
                    print(f"[Error] {e}")
                    os._exit(1)  # input() bloquea el hilo principal, salimos desde acá

                destino_local = "recibido_" + os.path.basename(nombre)
                with open(destino_local, "wb") as f:
                    f.write(datos_archivo)

                # Mostrar guardado del archivo y reimprimir prompt + texto parcial
                with input_lock:
                    cur = current_input
                print(f"[File] Guardado como: {destino_local}")
                sys.stdout.write(">" + cur)
                sys.stdout.flush()
                continue

            procesar_linea(linea)


# --------------PROGRAMA-------------------------
# Conectar al sv
host = sys.argv[1] if len(sys.argv) > 1 else "138.36.99.9"
# host = sys.argv[1] if len(sys.argv) > 1 else "127.0.0.1"
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
nombre = input("[Login] Quien sos?: ")
s.sendall(("LOGIN " + nombre + "\n").encode())
print(f"[Login] Login enviado: [{nombre}] a [{host}:{port}]")
respuesta = s.recv(1024).decode()
print(f"[Login] Respuesta del servidor: {respuesta}")
if respuesta.startswith("OK"):
    print(f"[Login] Entraste al chat como: {nombre}")
    s.sendall(("LIST\n").encode())
    respuesta = s.recv(1024).decode()
    print(f"{respuesta}")
else:
    print("[Error] Error en el login", respuesta)
    s.close()
    sys.exit()

# A partir de acá el socket lo lee solo el hilo receptor
hilo_receptor = threading.Thread(target=recibir_mensajes, args=(s,), daemon=True)
hilo_receptor.start()

# Loop: este hilo solo lee teclado y manda
while True:
    texto = read_input(">")
    estado = manejar_entrada(s, texto)

    if estado == "salir":
        break


# Cerrar la conexión
detener.set()
s.close()
print("[CLIENT] Conexión cerrada")
