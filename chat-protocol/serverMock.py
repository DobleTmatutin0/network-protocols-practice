"""
Server MOCK para probar el cliente del TP4.

NO es el server del TP (ese va en C). Es solo un banco de pruebas: responde a
los comandos del protocolo con respuestas simples, para que puedas desarrollar
y probar el cliente sin depender del server real.

Atiende un cliente a la vez y mantiene en memoria los usuarios registrados.

Uso:
    Terminal 1:  python mock_server.py
    Terminal 2:  python cliente.py
"""
import socket

HOST = "127.0.0.1"
PORT = 8888

# Estado en memoria: nombre de usuario -> id
usuarios = {}
proximo_id = 1


def procesar(linea):
    """Recibe una linea (sin el '\\n') y devuelve la respuesta del protocolo."""
    global proximo_id

    if not linea.strip():
        return "ERROR 9 linea vacia"

    # Separa el comando del resto. Ej: "MSG beto hola" -> ("MSG", "beto hola")
    partes = linea.split(" ", 1)
    cmd = partes[0].upper()
    arg = partes[1].strip() if len(partes) > 1 else ""

    if cmd == "REGISTER":
        if arg in usuarios:
            return "ERROR 2 usuario ya registrado"
        usuarios[arg] = proximo_id
        resp = f"OK {proximo_id}"
        proximo_id += 1
        return resp

    if cmd == "LOGIN":
        if arg not in usuarios:
            # Para que sea comodo de probar, lo registramos al vuelo.
            usuarios[arg] = proximo_id
            proximo_id += 1
        return "OK online"

    if cmd == "LIST":
        if usuarios:
            return "OK " + ", ".join(usuarios.keys())
        return "OK (no hay usuarios)"

    if cmd == "MSG":
        sub = arg.split(" ", 1)
        if len(sub) < 2:
            return "ERROR 3 formato: MSG <destino> <texto>"
        destino = sub[0]
        if destino not in usuarios:
            return "ERROR 1 destino inexistente"
        # OJO: este mock NO reenvia a otro cliente, solo simula el envio.
        return "OK enviado"

    if cmd == "LOGOUT":
        return "OK chau"

    return "ERROR 9 comando desconocido"


def atender(conn, addr):
    print(f"[+] Conexion de {addr}")
    buffer = ""
    while True:
        chunk = conn.recv(1024)
        if not chunk:
            break  # el cliente cerro la conexion
        buffer += chunk.decode()

        # TCP es un stream: en un mismo recv pueden venir varias lineas juntas,
        # o una linea a medias. Procesamos solo las lineas completas (con '\n').
        while "\n" in buffer:
            linea, buffer = buffer.split("\n", 1)
            print(f"    <- {linea!r}")
            respuesta = procesar(linea)
            print(f"    -> {respuesta!r}")
            conn.sendall((respuesta + "\n").encode())

    conn.close()
    print(f"[-] {addr} desconectado")


def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT))
    s.listen()
    print(f"MOCK escuchando en {HOST}:{PORT} ... (Ctrl+C para cortar)")
    try:
        while True:
            conn, addr = s.accept()
            atender(conn, addr)  # atiende un cliente a la vez
    except KeyboardInterrupt:
        print("\nCerrando mock.")
    finally:
        s.close()


if __name__ == "__main__":
    main()