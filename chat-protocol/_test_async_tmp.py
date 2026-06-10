"""Test descartable: verifica que el cliente muestre mensajes sin tener que enviar nada."""
import socket
import subprocess
import sys
import threading
import time

HOST, PORT = "127.0.0.1", 8888


def server():
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind((HOST, PORT))
    srv.listen(1)
    conn, _ = srv.accept()
    buf = b""
    while b"\n" not in buf:
        buf += conn.recv(1024)  # LOGIN
    conn.sendall(b"OK LOGIN\n")
    buf = b""
    while b"\n" not in buf:
        buf += conn.recv(1024)  # LIST
    conn.sendall(b"OK LIST tester\n")
    time.sleep(2)
    # Push NO solicitado: el cliente está quieto en el prompt
    conn.sendall(b"MSG servidor hola-async\n")
    time.sleep(4)
    conn.close()
    srv.close()


threading.Thread(target=server, daemon=True).start()
time.sleep(0.5)

p = subprocess.Popen(
    [sys.executable, "cliente.py", HOST],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
    encoding="utf-8",
)
try:
    p.stdin.write("tester\n")
    p.stdin.flush()
    time.sleep(4)  # el cliente queda quieto: el mensaje debe aparecer solo
    p.stdin.write("/quit\n")
    p.stdin.flush()
    out, _ = p.communicate(timeout=10)
except subprocess.TimeoutExpired:
    p.kill()
    out, _ = p.communicate()

print(out[-600:])
print("RESULTADO:", "ASYNC OK" if "hola-async" in out else "ASYNC FAIL")
