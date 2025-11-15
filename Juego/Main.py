import sys
import pygame
from UI_manager import UIManager
import Juego.UI.UI_Bienvenida as UI_Bienvenida
import Juego.UI.UI_Instrucciones as UI_Instrucciones
import Juego.UI.UI_Video as UI_Video
import Juego.UI.UI_Configuraciones as UI_Configuraciones
import Juego.UI.UI_Juego as UI_Juego


def main():
    pygame.init()
    pygame.mixer.init() 
    
    screen = pygame.display.set_mode((800, 460))
    pygame.display.set_caption('Bingo - Interfaz')
    clock = pygame.time.Clock()

   #MUSICA DE FONDO
    try:
        pygame.mixer.music.load('Musica.mp3')
        pygame.mixer.music.set_volume(0.5)  
        pygame.mixer.music.play(-1)  #loop
    except pygame.error as e:
        print(f"No se pudo cargar la música: {e}")

    manager = UIManager(screen)
    manager.register('bienvenida', UI_Bienvenida.UI_Bienvenida)
    manager.register('instrucciones', UI_Instrucciones.UI_Instrucciones)
    manager.register('video', UI_Video.UI_Video)
    manager.register('config', UI_Configuraciones.UI_Configuraciones)
    manager.register('juego', UI_Juego.UI_Juego)
    manager.set_view('bienvenida')

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