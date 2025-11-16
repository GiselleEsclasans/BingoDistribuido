from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
from urllib.parse import quote
import os

app = FastAPI(title="BINGODistribuido API", description="API para el sistema Bingo Distribuido")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

static_directory = "static"
if not os.path.exists(static_directory):
    os.makedirs(static_directory, exist_ok=True)
    videos_dir = os.path.join(static_directory, "videos")
    os.makedirs(videos_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory=static_directory), name="static")

class UsuarioRegistro(BaseModel):
    username: str
    email: str
    password: str

class UsuarioLogin(BaseModel): 
    username: str
    password: str

class SetOnlineModel(BaseModel):
    username: str
    online: bool

USUARIOS = {
    "admin": {"email": "admin@test.com", "password": "123", "online": False}
}


@app.post("/registro")
async def registrar_usuario(usuario: UsuarioRegistro):
    if usuario.username in USUARIOS:
        raise HTTPException(status_code=400, detail="El nombre de usuario ya existe")
        
    USUARIOS[usuario.username] = {
        "email": usuario.email,
        "password": usuario.password,
        "online": False
    }
    return {
        "message": f"Usuario {usuario.username} registrado!",
        "status": "success"
    }

@app.post("/login")
async def login_usuario(usuario: UsuarioLogin):
    user_en_db = USUARIOS.get(usuario.username)
    
    if not user_en_db:
        raise HTTPException(status_code=404, detail="Usuario no existe")
        
    if user_en_db["password"] != usuario.password:
        raise HTTPException(status_code=401, detail="Contraseña incorrecta")
        
    return {
        "status": "success",
        "message": "Login exitoso",
        "username": usuario.username
    }

@app.post('/set_online')
async def set_online(data: SetOnlineModel):
    user = USUARIOS.get(data.username)
    if not user:
        return {"status": "error", "message": "Usuario no registrado"}
    user['online'] = data.online
    return {"status": "success", "username": data.username, "online": data.online}

@app.get('/users')
async def listar_usuarios():
    return {"users": [{"username": k, "email": v['email'], "online": v['online']} for k, v in USUARIOS.items()]}

@app.get("/terminos")
async def obtener_terminos():
    return {
        "titulo": "Términos y Condiciones",
        "contenido": """
        <h4>1. Aceptación de Términos </h4>
        <p>Al utilizar Bingo Distribuido, aceptas cumplir con estos términos y condiciones:</p>
        
        <h4>2. Uso del Sistema</h4>
        <p>Bingo Distribuido es un sistema desarrollado con Pygame para fines educativos y de entretenimiento.</p>
        
        <h4>3. Elegibilidad</h4>
        <p>Debes ser mayor de 13 años para utilizar el sistema.</p>
        
        <h4>4. Propiedad Intelectual</h4>
        <p>Todo el código y contenido de Bingo Distribuido es propiedad de la Unimet como proyecto académico.</p>
        """,
    }

@app.get("/video")
async def obtener_video():
    return {
        "titulo": "Video Promocional",
        "descripcion": "Demostración del sistema de bingo desarrollado con Pygame",
        "url": "http://localhost:8000/static/videos/bingo-promo.mp4"
    }

@app.get("/videos/list")
async def listar_videos():
    videos_dir = Path("static/videos")
    print(videos_dir)
    if not videos_dir.exists():
        raise HTTPException(status_code=404, detail="Directorio de videos no encontrado")

    videos = []
    for video_file in videos_dir.glob("*.mp4"):
        videos.append({
            "nombre": video_file.name,
            "url": f"http://localhost:8000/videos/stream/{quote(video_file.name)}",
            "url_directa": f"http://localhost:8000/static/videos/{quote(video_file.name)}",
            "tamaño_mb": round(video_file.stat().st_size / (1024 * 1024), 2)
        })



    return {
        "total": len(videos),
        "videos": videos
    }




@app.get("/videos/stream/{filename}")
async def servir_video(filename: str):
    video_path = Path("static/videos") / filename
    if not video_path.exists() or not video_path.is_file():
        raise HTTPException(status_code=404, detail=f"Video '{filename}' no encontrado")

    return FileResponse(
        path=str(video_path),
        media_type="video/mp4",
        filename=filename
    )



@app.get("/instalacion")
async def obtener_instrucciones_instalacion():
    return {
        "titulo": "Instalación de Bingo Distribuido",
        "pasos": [
            "Asegúrate de tener Python 3.4 o superior instalado",
            "Descarga todos los archivos del proyecto Bingo Distribuido",
            "Abre una terminal en la carpeta del proyecto",
            "Instala Pygame: pip install pygame",
            "Ejecuta el archivo principal: python Main.py",
            "El juego se iniciará automáticamente con la interfaz de bienvenida y a disfrutar!"
        ],
        "requisitos": "Python 3.4+, Pygame, Windows/MacOS/Linux",
        "nota": "Todos los archivos deben mantenerse en la misma carpeta: Main.py, UI_Bienvenida.py, UI_Juego.py, Bingo.mp4, Musica.mp3, etc."
    }

@app.get("/uso")
async def obtener_instrucciones_uso():
    return {
        "titulo": "Cómo usar Bingo Distribuido",
        "descripcion": "Guía completa para utilizar el sistema de Bingo Distribuido",
        "pasos": [
            "Al iniciar el juego, verás la pantalla de bienvenida",
            "Navega por los diferentes menús y opciones disponibles",
            "En Configuraciones, elige el número de jugadores y modo de juego",
            "Revisa las Instrucciones para entender las reglas del bingo y del sistema",
            "Al iniciar el juego, cada jugador recibe un cartón automáticamente",
            "Los números se generan aleatoriamente y debes marcarlos en tu cartón",
            "Gana el primer jugador que complete el patrón establecido",
            "Puedes usar la interfaz de chat para comunicarte con otros jugadores!"
        ]
    }

@app.get("/")
async def root():
    return {"message": "API de BINGO Distribuido funcionando correctamente"}




if __name__ == "__main__":
    import uvicorn
    print("Usuarios de prueba cargados:")
    print(USUARIOS)
    uvicorn.run(app, host="0.0.0.0", port=8000)