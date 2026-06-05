# Chat Protocol - TP4

## 📋 Especificación del Protocolo

### Características
- **Tipo**: Protocolo de aplicación sobre TCP
- **Puerto**: 8888
- **Formato**: Texto basado, mensajes terminados con `\n`
- **Codificación**: UTF-8
- **Característica**: Cliente-Servidor centralizado con chat bidireccional

---

## 🔌 Conexión Inicial

```
Cliente → TCP connect a localhost:8888
        ↓
Servidor → acepta conexión
        ↓
Cliente → envía LOGIN
```

---

## 📨 Comandos del Protocolo

### 1️⃣ LOGIN - Autenticación

**Petición:**
```
LOGIN <nombre_usuario>\n
```

**Respuesta exitosa:**
```
OK LOGIN <id_usuario>\n
```

**Respuesta error:**
```
ERROR LOGIN Usuario ya existe\n
ERROR LOGIN Nombre vacío\n
```

**Ejemplo:**
```
C → LOGIN alice
S → OK LOGIN 1
```

---

### 2️⃣ LIST - Listar usuarios conectados

**Petición:**
```
LIST\n
```

**Respuesta:**
```
OK LIST <usuario1>,<usuario2>,...\n
```

**Ejemplo:**
```
C → LIST
S → OK LIST alice,bob,charlie
```

---

### 3️⃣ SEND - Enviar mensaje a otro usuario

**Petición:**
```
SEND <destinatario> <mensaje>\n
```

**Respuesta (confirmación al remitente):**
```
OK SEND\n
```

**Mensaje recibido (en el cliente destinatario):**
```
MSG <remitente> <timestamp> <mensaje>\n
```

**Ejemplo:**
```
C1 → SEND bob Hola, ¿cómo estás?
S  → OK SEND (a C1)
S  → MSG alice 12:34:56 Hola, ¿cómo estás? (a bob)
```

**Errores:**
```
ERROR SEND Usuario no existe
ERROR SEND Usuario no conectado
ERROR SEND Mensaje vacío
```

---

### 4️⃣ SENDFILE - Transferencia de archivos

**Petición:**
```
SENDFILE <destinatario> <nombre_archivo> <tamaño_bytes>\n
<contenido_archivo_binario>\n
```

**Respuesta (confirmación al remitente):**
```
OK SENDFILE\n
```

**Notificación al destinatario:**
```
FILE <remitente> <nombre_archivo> <tamaño_bytes>\n
<contenido_archivo_binario>\n
```

**Ejemplo:**
```
C1 → SENDFILE bob documento.txt 1234
C1 → [1234 bytes de contenido]
S  → OK SENDFILE (a C1)
S  → FILE alice documento.txt 1234 (a bob)
S  → [1234 bytes de contenido] (a bob)
```

**Errores:**
```
ERROR SENDFILE Usuario no existe
ERROR SENDFILE Archivo no encontrado
ERROR SENDFILE Tamaño muy grande
```

---

### 5️⃣ QUIT - Desconexión

**Petición:**
```
QUIT\n
```

**Respuesta:**
```
OK QUIT\n
```

Luego el servidor cierra la conexión.

---

## 🚨 Mensajes de Error Globales

Cualquier comando inválido:
```
ERROR Comando desconocido
```

Sin autenticación previa:
```
ERROR Debes hacer LOGIN primero
```

---

## 🔄 Flujo de una Sesión Típica

```
┌─────────────────────────────────────────┐
│ 1. Cliente se conecta (TCP)             │
├─────────────────────────────────────────┤
│ 2. Envía: LOGIN alice                   │
│    Recibe: OK LOGIN 1                   │
├─────────────────────────────────────────┤
│ 3. Envía: LIST                          │
│    Recibe: OK LIST bob,charlie          │
├─────────────────────────────────────────┤
│ 4. Envía: SEND bob Hola!                │
│    Recibe: OK SEND                      │
├─────────────────────────────────────────┤
│ 5. Recibe: MSG bob 12:34:56 Hola tú!    │
├─────────────────────────────────────────┤
│ 6. Envía: SENDFILE bob archivo.txt 500  │
│    Envía: [500 bytes]                   │
│    Recibe: OK SENDFILE                  │
├─────────────────────────────────────────┤
│ 7. Envía: QUIT                          │
│    Recibe: OK QUIT                      │
│    Conexión cierra                      │
└─────────────────────────────────────────┘
```

---

## 💾 Limitaciones

- Máximo 10 clientes simultáneos
- Máximo 50 caracteres de nombre de usuario
- Máximo 1000 caracteres por mensaje
- Máximo 5 MB por archivo
- Máximo 5 archivos en cola de espera

---

## 📁 Estructura del Repositorio

```
/
├── README.md              (este archivo - especificación)
├── cliente.py             (cliente en Python)
├── chat-protocol/
│   └── chat-sv.c         (servidor en C)
└── trivial-file-transfer-protocol-TFTP/
    ├── tftp-client.c
    └── tftp-server.c
```