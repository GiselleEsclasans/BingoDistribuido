import sys
import pygame
import os
from UI_manager import UIManager
import UI.UI_Login as UI_Login
import UI.UI_Bienvenida as UI_Bienvenida
import UI.UI_Instrucciones as UI_Instrucciones
import UI.UI_Video as UI_Video
import UI.UI_Configuraciones as UI_Configuraciones
import UI.UI_Juego as UI_Juego

def get_asset_path(filename):
    """Obtener la ruta correcta para los archivos de assets"""
    possible_paths = [
        filename,
        os.path.join('Assets', filename),
        os.path.join('..', 'Assets', filename),
        os.path.join('Juego', 'Assets', filename),
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return path
    
    print(f"⚠️ No se encontró: {filename}")
    return filename

def main():
    pygame.init()
    pygame.mixer.init() 
    
    screen = pygame.display.set_mode((800, 460)) 
    pygame.display.set_caption('Bingo - Interfaz')
    clock = pygame.time.Clock()

    try:
        music_path = get_asset_path('Musica.mp3')
        pygame.mixer.music.load(music_path)
        pygame.mixer.music.set_volume(0.5)  
        pygame.mixer.music.play(-1)
        print(f"🎵 Música cargada desde: {music_path}")
    except pygame.error as e:
        print(f"❌ No se pudo cargar la música: {e}")

    manager = UIManager(screen) 
    
    manager.register('login', UI_Login.UI_Login) 
    manager.register('bienvenida', UI_Bienvenida.UI_Bienvenida)
    manager.register('instrucciones', UI_Instrucciones.UI_Instrucciones)
    manager.register('video', UI_Video.UI_Video)
    manager.register('config', UI_Configuraciones.UI_Configuraciones)
    manager.register('juego', UI_Juego.UI_Juego)
    
    manager.set_view('login') 

    running = True
    while running:
        dt = clock.tick(30) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            manager.handle_event(event)

        manager.update(dt)
        manager.render()
        pygame.display.flip()

    pygame.mixer.music.stop()  
    pygame.quit()

if __name__ == '__main__':
    main()