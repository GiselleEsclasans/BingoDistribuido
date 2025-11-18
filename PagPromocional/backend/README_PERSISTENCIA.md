# Persistencia de Usuarios - Bingo Distribuido

## 📋 Descripción

Los usuarios registrados en la página promocional ahora se guardan automáticamente en un archivo JSON llamado `usuarios_registrados.json`.

## 🔄 Funcionamiento

### Al iniciar la API
- Se carga automáticamente el archivo `usuarios_registrados.json` si existe
- Si el archivo no existe, se crea uno nuevo vacío (o con usuario admin en `api.py`)
- Se muestra un mensaje en consola indicando cuántos usuarios fueron cargados

### Durante la ejecución
Los usuarios se guardan automáticamente en los siguientes casos:
- ✅ Cuando se registra un nuevo usuario (`POST /registro`)
- ✅ Cuando un usuario cambia su estado online/offline (`POST /set_online`)

### Al cerrar la API
- Se ejecuta un evento de shutdown que guarda todos los usuarios
- Se muestra un mensaje confirmando que los datos fueron guardados

## 📁 Formato del archivo JSON

```json
{
  "admin": {
    "email": "admin@test.com",
    "password": "123",
    "online": false
  },
  "usuario1": {
    "email": "usuario1@example.com",
    "password": "password123",
    "online": false
  }
}
```

## 🚀 Uso

### Iniciar la API

#### Usando `api.py` (versión completa con más endpoints):
```bash
cd PagPromocional/backend
python api.py
```

#### Usando `mainPag.py` (versión simplificada):
```bash
cd PagPromocional/backend
python mainPag.py
```

### Ubicación del archivo
El archivo `usuarios_registrados.json` se crea en el mismo directorio donde se ejecuta la API:
```
PagPromocional/backend/usuarios_registrados.json
```

## 🔒 Notas de Seguridad

**⚠️ IMPORTANTE:** Este sistema guarda las contraseñas en texto plano en el archivo JSON. 

Para un sistema en producción, deberías:
- Usar hash de contraseñas (bcrypt, argon2, etc.)
- Implementar tokens JWT para autenticación
- Usar una base de datos real (PostgreSQL, MongoDB, etc.)

## 🧪 Pruebas

Para verificar que la persistencia funciona:

1. Inicia la API
2. Registra algunos usuarios desde el frontend
3. Cierra la API (Ctrl+C)
4. Verifica que el archivo `usuarios_registrados.json` existe
5. Vuelve a iniciar la API
6. Verifica en consola que se cargaron los usuarios
7. Los usuarios registrados deberían estar disponibles para login

## 📝 Logs en Consola

Al iniciar:
```
✅ 3 usuarios cargados desde usuarios_registrados.json
```

Al registrar un usuario:
```
💾 Usuarios guardados en usuarios_registrados.json
```

Al cerrar:
```
🔄 Cerrando API, guardando usuarios...
💾 Usuarios guardados en usuarios_registrados.json
✅ Usuarios guardados correctamente
```

