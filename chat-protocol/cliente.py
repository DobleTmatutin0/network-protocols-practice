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
historial = []  # comandos enviados, del más viejo al más nuevo (para las flechas ↑↓)

try:
    import msvcrt

    def getch():
        ch = msvcrt.getwch()
        if ch in ("\x00", "\xe0"):              # prefijo de tecla especial
            ch2 = msvcrt.getwch()
            return {"H": "UP", "P": "DOWN", "K": "LEFT", "M": "RIGHT",
                    "G": "HOME", "O": "END", "S": "DELETE"}.get(ch2, "IGNORE")
        if ch in ("\r", "\n"):
            return "ENTER"
        if ch == "\x08":
            return "BACKSPACE"
        if ch == "\x03":                        # Ctrl-C
            raise KeyboardInterrupt
        if ord(ch) < 32:                        # otros caracteres de control
            return "IGNORE"
        return ch                               # carácter imprimible normal
except Exception:
    import tty
    import termios

    def getch():
        fd = sys.stdin.fileno()
        old = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
            if ch == "\x1b":                    # ESC: posible flecha ESC [ A/B/C/D
                ch2 = sys.stdin.read(1)
                if ch2 == "[":
                    ch3 = sys.stdin.read(1)
                    if ch3 == "3":
                        sys.stdin.read(1)       # consumir el '~' final de Delete
                        return "DELETE"
                    return {"A": "UP", "B": "DOWN", "C": "RIGHT", "D": "LEFT",
                            "H": "HOME", "F": "END"}.get(ch3, "IGNORE")
                return "IGNORE"
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old)
        if ch in ("\r", "\n"):
            return "ENTER"
        if ch in ("\x7f", "\x08"):
            return "BACKSPACE"
        if ch == "\x03":
            raise KeyboardInterrupt
        if ord(ch) < 32:
            return "IGNORE"
        return ch


def read_input(prompt):
    """Lee la línea manteniendo el buffer parcial en `current_input` (para que el
    hilo receptor pueda reimprimir lo que el usuario escribe) y soportando edición
    con cursor (←→ Home End Delete Backspace) e historial (↑↓), como hacía input().
    """
    global current_input
    buf = []          # caracteres de la línea (lista para insertar/borrar en el medio)
    pos = 0           # posición del cursor dentro de buf (0..len)
    hist_index = len(historial)   # apunta a la "línea nueva" (después del último)
    borrador = []                 # lo que se tipeaba antes de empezar a navegar historial

    def redibujar():
        # Reescribe la línea entera y deja el cursor en `pos`
        texto = "".join(buf)
        sys.stdout.write("\r\033[K" + prompt + texto)
        atras = len(buf) - pos
        if atras > 0:
            sys.stdout.write(f"\033[{atras}D")
        sys.stdout.flush()

    sys.stdout.write(prompt)
    sys.stdout.flush()

    while True:
        key = getch()

        if key == "ENTER":
            sys.stdout.write("\n")
            sys.stdout.flush()
            texto = "".join(buf)
            if texto.strip() and (not historial or historial[-1] != texto):
                historial.append(texto)
            with input_lock:
                current_input = ""
            return texto

        elif key == "BACKSPACE":
            if pos > 0:
                del buf[pos - 1]
                pos -= 1
                redibujar()
        elif key == "DELETE":
            if pos < len(buf):
                del buf[pos]
                redibujar()
        elif key == "LEFT":
            if pos > 0:
                pos -= 1
                redibujar()
        elif key == "RIGHT":
            if pos < len(buf):
                pos += 1
                redibujar()
        elif key == "HOME":
            if pos != 0:
                pos = 0
                redibujar()
        elif key == "END":
            if pos != len(buf):
                pos = len(buf)
                redibujar()
        elif key == "UP":
            if hist_index > 0:
                if hist_index == len(historial):
                    borrador = buf[:]          # guardar lo que se estaba escribiendo
                hist_index -= 1
                buf = list(historial[hist_index])
                pos = len(buf)
                redibujar()
        elif key == "DOWN":
            if hist_index < len(historial):
                hist_index += 1
                if hist_index == len(historial):
                    buf = borrador[:]          # volver al borrador
                else:
                    buf = list(historial[hist_index])
                pos = len(buf)
                redibujar()
        elif key == "IGNORE":
            pass
        else:
            # carácter imprimible: insertarlo en la posición del cursor
            buf.insert(pos, key)
            pos += 1
            redibujar()

        with input_lock:
            current_input = "".join(buf)


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
