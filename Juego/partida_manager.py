import threading
import time
import random
from bingo_utils import get_letter_for_number

class ManejadorPartida(threading.Thread):
    def __init__(self, partida_id, server_instance):
        """
        Inicializa el hilo que maneja la lógica de una sola partida.
        :param partida_id: El ID de la partida a manejar.
        :param server_instance: La instancia principal de GameServer.
        """
        super().__init__(daemon=True)
        self.partida_id = partida_id
        self.server = server_instance
        self.partida = self.server.partidas.get(partida_id)

    def run(self):
        """El bucle principal de la partida (antes era 'manejar_partida')"""
        if not self.partida:
            print(f"Error: Hilo de partida {self.partida_id} no pudo encontrar los datos.")
            return

        print(f"Iniciando hilo para partida {self.partida_id}...")
        tiempo_espera = 30
        inicio_espera = time.time()
        min_jugadores = self.partida.get('min_jugadores', 2)

        while len(self.partida['jugadores']) < min_jugadores:
            if not self.partida['activa']:
                print(f"Partida {self.partida_id} cancelada durante la espera.")
                return

            if time.time() - inicio_espera > tiempo_espera:
                if len(self.partida['jugadores']) < 1:
                    print(f"Partida {self.partida_id} cerrada por falta de jugadores.")
                    self.server.cerrar_partida(self.partida_id)
                    return
                print(f"Partida {self.partida_id} iniciando por tiempo de espera con {len(self.partida['jugadores'])} jugador(es).")
                break

            time.sleep(1)

        self.server.broadcast_partida(self.partida_id, {
            "action": "game_start",
            "message": "Bingo ha comenzado!"
        })
        
        self.server.actualizar_lista_jugadores(self.partida_id)
        
        numeros_posibles = list(range(1, 76))
        random.shuffle(numeros_posibles)
        turno_actual = 0
        
        for numero in numeros_posibles:
            if not self.partida['activa']:
                print(f"Partida {self.partida_id} detenida (alguien ganó o se vació).")
                break 
            self.partida['numeros_salidos'].append(numero)
            
            etiqueta = f"{get_letter_for_number(numero)}-{numero}"
            
            
            self.server.broadcast_partida(self.partida_id, {
                "action": "number_drawn",
                "number": numero,
                "label": etiqueta  
            })
   
            
            
            time.sleep(3)

        if self.partida['activa']:
            self.server.broadcast_partida(self.partida_id, {
                "action": "game_over",
                "winner": "Nadie",
                "reason": "Se acabaron los números"
            })
            self.server.cerrar_partida(self.partida_id)