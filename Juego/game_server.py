import socket
import threading
import json
import time
from client_handler import ClientHandler

class GameServer:
    def __init__(self, host='localhost', port=6000):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = host
        self.port = port
        self.jugadores = {}  
        self.partidas = {}   
        
    def iniciar(self):
        """Bucle principal que acepta nuevas conexiones."""
        self.server.bind((self.host, self.port))
        self.server.listen()
        print(f"🎮 Servidor de Juego escuchando en {self.host}:{self.port}")
        
        while True:
            try:
                cliente, direccion = self.server.accept()
                print(f"✅ Nueva conexión de juego desde {direccion}")
     
                handler = ClientHandler(cliente, direccion, self)
                handler.start()
                
            except Exception as e:
                print(f"Error aceptando conexión: {e}")

    def broadcast_partida(self, partida_id, mensaje):
        """Enviar mensaje a todos los jugadores de una partida."""
        if partida_id not in self.partidas:
            return
            
        partida = self.partidas[partida_id]
        for jugador_nick in list(partida['jugadores'].keys()): 
            if jugador_nick in self.jugadores:
                try:
                    socket_jugador = self.jugadores[jugador_nick]['socket']
                    mensaje_enviado = json.dumps(mensaje) + '\n'
                    socket_jugador.send(mensaje_enviado.encode('utf-8'))

                except (BrokenPipeError, ConnectionResetError, OSError):
                    print(f"Error de conexión con {jugador_nick} (broadcast). Removiendo.")
                    self.remover_jugador(jugador_nick)

    def actualizar_lista_jugadores(self, partida_id):
        """Enviar lista actualizada de jugadores a todos en una partida."""
        if partida_id not in self.partidas:
            return
            
        partida = self.partidas[partida_id]
        jugadores_lista = list(partida['jugadores'].keys())
        
        self.broadcast_partida(partida_id, {
            "action": "player_list",
            "players": jugadores_lista
        })
        
    def remover_jugador(self, jugador_nick):
        """Remover jugador desconectado del servidor y su partida."""
        if jugador_nick in self.jugadores:
            partida_id = self.jugadores[jugador_nick].get('partida_id')
            
            try:
                self.jugadores[jugador_nick]['socket'].close()
            except:
                pass
                
            del self.jugadores[jugador_nick]
     
            if partida_id and partida_id in self.partidas:
                partida = self.partidas[partida_id]
                if jugador_nick in partida['jugadores']:
                    del partida['jugadores'][jugador_nick]
                    
                    self.broadcast_partida(partida_id, {
                        "action": "player_left",
                        "player": jugador_nick,
                        "message": f"{jugador_nick} abandonó la partida"
                    })
                    
                    self.actualizar_lista_jugadores(partida_id)
                    
                    if not partida['jugadores'] and partida['activa']:
                        print(f"Cerrando partida {partida_id} por estar vacía.")
                        self.cerrar_partida(partida_id)

    def cerrar_partida(self, partida_id):
        """Limpia una partida del servidor."""
        if partida_id in self.partidas:
            self.partidas[partida_id]['activa'] = False
            if partida_id in self.partidas:
                del self.partidas[partida_id]
                print(f"Partida {partida_id} eliminada del servidor.")

if __name__ == "__main__":
    game_server = GameServer()
    game_server.iniciar()