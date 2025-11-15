from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="BINGODistribuido API", description="API para el sistema Bingo Distribuido")

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

# Modelo de datos
class UsuarioRegistro(BaseModel):
    username: str
    email: str
    password: str

# Endpoint de registro
@app.post("/registro")
async def registrar_usuario(usuario: UsuarioRegistro):
    return {
        "message": f"Usuario {usuario.username} registrado exitosamente en Bingo Distribuido!",
        "email": usuario.email,
        "status": "active"
    }

# Endpoint de términos y condiciones
@app.get("/terminos")
async def obtener_terminos():
    return {
        "titulo": "Términos y Condiciones",
        "contenido": """
        <h4>1. Aceptación de Términos</h4>
        <p>Al utilizar Bingo Distribuido, aceptas cumplir con estos términos y condiciones:</p>
        
        <h4>2. Uso del Sistema</h4>
        <p>Bingo Distribuido es un sistema desarrollado con Pygame para fines educativos y de entretenimiento.</p>
        
        <h4>3. Elegibilidad</h4>
        <p>Debes ser mayor de 13 años para utilizar el sistema.</p>
        
        <h4>4. Propiedad Intelectual</h4>
        <p>Todo el código y contenido de Bingo Distribuido es propiedad de la Unimet como proyecto académico.</p>
        
      
        """,
        
    }

# Endpoint del video
@app.get("/video")
async def obtener_video():
    return {
        "titulo": "Video Promocional",
        "descripcion": "Demostración del sistema de bingo desarrollado con Pygame",
        "url": "http://localhost:8000/static/videos/bingo-promo.mp4"
    }

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

# Endpoint de salud
@app.get("/")
async def root():
    return {"message": "API de BINGO Distribuido funcionando correctamente"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)