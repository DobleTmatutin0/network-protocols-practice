# Chat Protocol - TP4

## 📋 Especificación del Protocolo

### Características

* **Tipo:** Protocolo de aplicación sobre TCP.
* **Puerto por defecto:** 8888.
* **Formato:** Texto basado en líneas terminadas con `\n`.
* **Codificación:** UTF-8.
* **Arquitectura:** Cliente-Servidor centralizado.
* **Mensajería:** Privada, broadcast y transferencia de archivos.

---

## 🔌 Conexión Inicial

Al conectarse al servidor, el cliente debe autenticarse mediante el comando `LOGIN`.

```
Cliente → TCP connect
Servidor → acepta conexión
Cliente → LOGIN <usuario>
Servidor → OK
```

Cualquier comando enviado antes del login será rechazado:

```
ERROR Debe hacer LOGIN primero
```

---

## 📨 Comandos del Protocolo

### 1️⃣ LOGIN

Permite registrar un nombre de usuario para la sesión.

**Petición**

```
LOGIN <nombre_usuario>\n
```

**Respuesta exitosa**

```
OK
```

**Respuesta de error**

```
ERROR LOGIN Nombre inválido
```

**Ejemplo**

```
C → LOGIN alice
S → OK
```

---

### 2️⃣ LIST

Obtiene la lista de usuarios conectados.

**Petición**

```
LIST\n
```

**Respuesta**

```
Usuarios conectados: alice,bob,charlie
```

**Ejemplo**

```
C → LIST
S → Usuarios conectados: alice,bob,charlie
```

---

### 3️⃣ MSG

Envía un mensaje privado a otro usuario.

**Petición**

```
MSG <destinatario> <mensaje>\n
```

**Confirmación al remitente**

```
OK MSG
```

**Mensaje recibido por el destinatario**

```
MSG <remitente> <mensaje>
```

**Ejemplo**

```
C1 → MSG bob Hola Bob
S  → OK MSG

S  → MSG alice Hola Bob
```

**Errores**

```
ERROR Usuario no encontrado
ERROR Formato: MSG <destino> <mensaje>
```

---

### 4️⃣ ALL

Envía un mensaje a todos los usuarios conectados excepto al remitente.

**Petición**

```
ALL <mensaje>\n
```

**Confirmación**

```
OK ALL
```

**Mensaje recibido por los demás clientes**

```
MSG <remitente> <mensaje>
```

**Ejemplo**

```
C → ALL Hola a todos

S → OK ALL

Otros clientes reciben:
MSG alice Hola a todos
```

---

### 5️⃣ FILE

Permite transferir archivos entre usuarios.

**Cabecera enviada por el remitente**

```
FILE <destinatario> <nombre_archivo> <tam_bytes>\n
```

**Confirmación del servidor**

```
OK FILE
```

Tras recibir la confirmación, el cliente transmite exactamente `<tam_bytes>` bytes.

**Cabecera enviada al destinatario**

```
FILE <remitente> <nombre_archivo> <tam_bytes>\n
```

A continuación se envían los bytes del archivo.

**Ejemplo**

```
C1 → FILE bob informe.pdf 2048

S  → OK FILE

C1 → [2048 bytes]

S  → FILE alice informe.pdf 2048
S  → [2048 bytes]
```

**Errores**

```
ERROR Usuario no encontrado
ERROR Formato: FILE <destino> <nombre> <tam>
ERROR FILE
```

---

### 6️⃣ PING

Permite verificar conectividad con el servidor.

**Petición**

```
PING
```

**Respuesta**

```
PONG
```

**Ejemplo**

```
C → PING
S → PONG
```

---

### 7️⃣ QUIT

Finaliza la sesión.

**Petición**

```
QUIT
```

**Respuesta**

```
OK QUIT
```

Luego el servidor cierra la conexión.

---

## 🚨 Errores Globales

Comando desconocido:

```
ERROR Comando desconocido
```

Intento de usar comandos sin autenticación:

```
ERROR Debe hacer LOGIN primero
```

---

## 🔄 Flujo de una Sesión Típica

```
1. Cliente conecta por TCP

2. LOGIN alice
   ← OK

3. LIST
   ← Usuarios conectados: bob,charlie

4. MSG bob Hola Bob
   ← OK MSG

5. ALL Hola a todos
   ← OK ALL

6. FILE bob documento.txt 500
   ← OK FILE
   → [500 bytes]

7. PING
   ← PONG

8. QUIT
   ← OK QUIT
```

---

## 💾 Limitaciones

* Máximo 10 clientes simultáneos.
* Longitud máxima de nombre de usuario: 31 caracteres.
* Comunicación basada en TCP.
* Transferencia de archivos mediante streaming binario sobre la misma conexión.

---

## 📁 Estructura del Repositorio

```
chat-protocol/
├── README.md
├── chat-sv.c
├── client.h
└── cliente.py
```
