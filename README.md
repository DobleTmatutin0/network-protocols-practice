# Chat Protocol - TP4

## 📋 Especificación del Protocolo

### Características

* **Tipo:** Protocolo de aplicación sobre TCP.
* **Puerto por defecto:** 8888.
* **Formato:** Mensajes de texto terminados en `\n`.
* **Codificación:** UTF-8.
* **Arquitectura:** Cliente-Servidor centralizado.
* **Máximo de clientes simultáneos:** 10.

---

## 🔐 Autenticación

Todo cliente debe autenticarse mediante el comando `LOGIN` antes de utilizar cualquier otro comando del protocolo.

Si un cliente intenta ejecutar otro comando sin haberse autenticado, el servidor responderá:

```text
ERROR Debe hacer LOGIN primero
```

---

## 🔌 Conexión Inicial

```text
Cliente → TCP connect
        ↓
Servidor → acepta conexión
        ↓
Cliente → LOGIN <usuario>
        ↓
Servidor → OK
```

---

## 📨 Comandos del Protocolo

### 1️⃣ LOGIN

Permite registrar un nombre de usuario en el servidor.

#### Petición

```text
LOGIN <nombre_usuario>\n
```

#### Respuesta exitosa

```text
OK\n
```

#### Respuesta de error

```text
ERROR LOGIN Nombre inválido\n
```

#### Ejemplo

```text
C → LOGIN alice
S → OK
```

---

### 2️⃣ LIST

Solicita la lista de usuarios conectados.

#### Petición

```text
LIST\n
```

#### Respuesta

```text
Usuarios conectados: alice,bob,charlie\n
```

#### Ejemplo

```text
C → LIST
S → Usuarios conectados: alice,bob,charlie
```

---

### 3️⃣ MSG

Envía un mensaje privado a otro usuario conectado.

#### Petición

```text
MSG <destinatario> <mensaje>\n
```

#### Confirmación al remitente

```text
OK MSG\n
```

#### Mensaje recibido por el destinatario

```text
MSG <remitente> <mensaje>\n
```

#### Ejemplo

```text
C1 → MSG bob Hola Bob
S  → OK MSG

S  → MSG alice Hola Bob
```

#### Errores

```text
ERROR Usuario no encontrado\n
ERROR Formato: MSG <destino> <mensaje>\n
```

---

### 4️⃣ ALL

Envía un mensaje a todos los usuarios conectados excepto al remitente.

#### Petición

```text
ALL <mensaje>\n
```

#### Confirmación

```text
OK ALL\n
```

#### Mensaje recibido por los demás usuarios

```text
MSG <remitente> <mensaje>\n
```

#### Ejemplo

```text
C1 → ALL Hola a todos
S  → OK ALL

C2 ← MSG alice Hola a todos
C3 ← MSG alice Hola a todos
```

---

### 5️⃣ PING

Permite verificar que la conexión sigue activa.

#### Petición

```text
PING\n
```

#### Respuesta

```text
PONG
```

#### Ejemplo

```text
C → PING
S → PONG
```

---

### 6️⃣ QUIT

Finaliza la sesión y cierra la conexión.

#### Petición

```text
QUIT\n
```

#### Respuesta

```text
OK QUIT\n
```

Luego el servidor cierra la conexión.

#### Ejemplo

```text
C → QUIT
S → OK QUIT
```

---

## 🚨 Errores Globales

### Cliente no autenticado

```text
ERROR Debe hacer LOGIN primero
```

### Comando desconocido

```text
ERROR Comando desconocido
```

---

## 🔄 Flujo de una Sesión Típica

```text
┌───────────────────────────────────────┐
│ Cliente se conecta por TCP            │
├───────────────────────────────────────┤
│ LOGIN alice                           │
│ OK                                    │
├───────────────────────────────────────┤
│ LIST                                  │
│ Usuarios conectados: bob,charlie      │
├───────────────────────────────────────┤
│ MSG bob Hola Bob                      │
│ OK MSG                                │
├───────────────────────────────────────┤
│ ALL Hola a todos                      │
│ OK ALL                                │
├───────────────────────────────────────┤
│ PING                                  │
│ PONG                                  │
├───────────────────────────────────────┤
│ QUIT                                  │
│ OK QUIT                               │
└───────────────────────────────────────┘
```

---

## 💾 Limitaciones

* Máximo 10 clientes simultáneos.
* Máximo 31 caracteres para nombres de usuario (`MAX_USERNAME = 32`, incluyendo `\0`).
* Tamaño máximo de mensaje limitado por `BUFFER_SIZE`.
* Comunicación basada en texto plano sobre TCP.

---

## 📁 Estructura del Repositorio

```text
chat-protocol/
├── README.md
├── cliente.py
├── client.h
└── chat-sv.c
```
