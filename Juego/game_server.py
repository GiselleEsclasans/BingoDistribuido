import socket
import threading
import json
import random
import time
from datetime import datetime

class GameServer:
    def __init__(self, host='localhost', port=6000):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = host
        self.port = port
        self.jugadores = {}  
        self.partidas = {}   
        
    def generar_carton(self):
        """Generar un cartón de bingo 3x5 con números únicos"""
        carton = []
        while len(carton) < 25: 
            num = random.randint(1, 75)
            if num not in carton:
                carton.append(num)
        return carton
    
    def verificar_patron_ganador(self, carton, numeros_marcados, modo_juego):
        """Verificar si un cartón tiene patrón ganador"""
        
        marcados_set = set(numeros_marcados)
        carton_marcado = [carton[i] in marcados_set for i in range(25)]

        if modo_juego == "rapido":
            lineas = [
                [0, 1, 2, 3, 4], [5, 6, 7, 8, 9], [10, 11, 12, 13, 14], [15, 16, 17, 18, 19], [20, 21, 22, 23, 24],
                [0, 5, 10, 15, 20], [1, 6, 11, 16, 21], [2, 7, 12, 17, 22], [3, 8, 13, 18, 23], [4, 9, 14, 19, 24],
                [0, 6, 12, 18, 24], [4, 8, 12, 16, 20]
            ]
            return any(all(carton_marcado[i] for i in linea) for linea in lineas)
            
        elif modo_juego == "regular":
            patron_regular = [0, 4, 12, 20, 24]
            return all(carton_marcado[i] for i in patron_regular)
            
        elif modo_juego == "blackout":
            return all(carton_marcado)
    
    def manejar_partida(self, partida_id):
        """Manejar la lógica de una partida específica"""
        if partida_id not in self.partidas:
            print(f"Error: Partida {partida_id} no encontrada al iniciar.")
            return
            
        partida = self.partidas[partida_id]
        
        tiempo_espera = 30 
        inicio_espera = time.time()
        
        while len(partida['jugadores']) < partida['max_jugadores']:
            if not partida['activa']: 
                return
            if time.time() - inicio_espera > tiempo_espera:
                if len(partida['jugadores']) < 1:
                    print(f"Partida {partida_id} cerrada por falta de jugadores.")
                    partida['activa'] = False
                    del self.partidas[partida_id]
                    return
                break
            time.sleep(1)

        self.broadcast_partida(partida_id, {
            "action": "game_start",
            "message": f"¡La partida ha comenzado! Jugadores: {len(partida['jugadores'])}/{partida['max_jugadores']}"
        })
        
        self.actualizar_lista_jugadores(partida_id)
        
        numeros_posibles = list(range(1, 76))
        random.shuffle(numeros_posibles)
        
        turno_actual = 0
        
        for numero in numeros_posibles:
            if not partida['activa']:
                break
                
            partida['numeros_salidos'].append(numero)
            
            jugadores_lista = list(partida['jugadores'].keys())
            if jugadores_lista:
                jugador_turno = jugadores_lista[turno_actual]
                self.broadcast_partida(partida_id, {
                    "action": "player_turn",
                    "player": jugador_turno
                })
                turno_actual = (turno_actual + 1) % len(jugadores_lista)
            
            self.broadcast_partida(partida_id, {
                "action": "number_drawn",
                "number": numero
            })
            
            for nick, datos_jugador in partida['jugadores'].items():
                if numero in datos_jugador['carton']:
                    if numero not in datos_jugador['numeros_marcados']:
                         datos_jugador['numeros_marcados'].append(numero)
            
            time.sleep(3)

        if partida['activa']:
            partida['activa'] = False
            self.broadcast_partida(partida_id, {
                "action": "game_over",
                "winner": "Nadie",
                "reason": "Se acabaron los números"
            })
    
    def actualizar_lista_jugadores(self, partida_id):
        """Enviar lista actualizada de jugadores a todos"""
        if partida_id not in self.partidas:
            return
            
        partida = self.partidas[partida_id]
        jugadores_lista = list(partida['jugadores'].keys())
        
        self.broadcast_partida(partida_id, {
            "action": "player_list",
            "players": jugadores_lista
        })
    
    def broadcast_partida(self, partida_id, mensaje):
        """Enviar mensaje a todos los jugadores de una partida"""
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
                    print(f"Error de conexión con {jugador_nick}. Removiendo.")
                    self.remover_jugador(jugador_nick)
    
    def remover_jugador(self, jugador_nick):
        """Remover jugador desconectado"""
        if jugador_nick in self.jugadores:
            partida_id = self.jugadores[jugador_nick].get('partida_id')
            socket_jugador = self.jugadores[jugador_nick]['socket']
            
            try:
                socket_jugador.close()
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
                    
                    if not partida['jugadores']:
                        print(f"Cerrando partida {partida_id} por estar vacía.")
                        partida['activa'] = False
                        if partida_id in self.partidas:
                            del self.partidas[partida_id]
    
    def manejar_cliente(self, cliente, direccion):
        """Manejar la comunicación con un cliente específico"""
        jugador_nick = None
        buffer = "" 

        try:
            while True:
                datos = cliente.recv(1024).decode('utf-8')
                if not datos:
                    break 
                buffer += datos
 
                while '\n' in buffer:
                    mensaje_str, buffer = buffer.split('\n', 1)
                    
                    if not mensaje_str:
                        continue
                        
                    try:
                        mensaje = json.loads(mensaje_str)
                    except json.JSONDecodeError:
                        print(f"Error: JSON malformado de {direccion}: {mensaje_str}")
                        continue
                
                    action = mensaje.get('action')
                    
                    if action == 'join_game':
                        jugador_nick = mensaje.get('nickname')
                        jugadores = int(mensaje.get('players'))
                        modo_juego = mensaje.get('game_mode')
                        
                        if not jugador_nick:
                            continue

                        if jugador_nick in self.jugadores:
                            self.remover_jugador(jugador_nick)

                        partida_id = None
                        for pid, pdata in self.partidas.items():
                            if (pdata['max_jugadores'] == jugadores and
                                pdata['modo_juego'] == modo_juego and
                                len(pdata['jugadores']) < pdata['max_jugadores'] and
                                pdata['activa']):
                                partida_id = pid
                                break
                        
                        if not partida_id:
                            partida_id = f"partida_{modo_juego}_{jugadores}p_{time.time()}"
                            self.partidas[partida_id] = {
                                'id': partida_id,
                                'max_jugadores': jugadores,
                                'modo_juego': modo_juego,
                                'jugadores': {},
                                'numeros_salidos': [],
                                'activa': True
                            }
                            print(f"Creando nueva partida: {partida_id}")
                            threading.Thread(target=self.manejar_partida, 
                                           args=(partida_id,), daemon=True).start()
                        
                        carton = self.generar_carton()
                        self.partidas[partida_id]['jugadores'][jugador_nick] = {
                            'carton': carton,
                            'numeros_marcados': [] 
                        }
                        
                        self.jugadores[jugador_nick] = {
                            'socket': cliente,
                            'partida_id': partida_id
                        }
                        
                        respuesta = {
                            "status": "success",
                            "carton": carton,
                            "partida_id": partida_id
                        }
                        
                        cliente.send((json.dumps(respuesta) + '\n').encode('utf-8'))
                        
                        self.broadcast_partida(partida_id, {
                            "action": "player_joined",
                            "player": jugador_nick,
                            "message": f"{jugador_nick} se unió a la partida"
                        })
                        
                        self.actualizar_lista_jugadores(partida_id)
                    
                    elif action == 'call_bingo':
                        if not jugador_nick or jugador_nick not in self.jugadores:
                            continue
                            
                        partida_id = self.jugadores[jugador_nick]['partida_id']
                        if partida_id not in self.partidas:
                            continue
                            
                        partida = self.partidas[partida_id]

                        if not partida['activa']:
                            continue
                            
                        datos_jugador = partida['jugadores'][jugador_nick]

                        if self.verificar_patron_ganador(datos_jugador['carton'],
                                                         datos_jugador['numeros_marcados'],
                                                         partida['modo_juego']):
                            
                            partida['activa'] = False 
                            
                            self.broadcast_partida(partida_id, {
                                "action": "bingo_called",
                                "winner": jugador_nick,
                                "reason": f"BINGO - Modo {partida['modo_juego']}"
                            })
                            
                            self.broadcast_partida(partida_id, {
                                "action": "game_over",
                                "winner": jugador_nick
                            })
                            

                        else:
                            cliente.send((json.dumps({
                                "action": "chat_message",
                                "nickname": "Sistema",
                                "message": "¡BINGO Falso! Sigues jugando."
                            }) + '\n').encode('utf-8'))
                    
                    elif action == 'chat_message':
                        if not jugador_nick or jugador_nick not in self.jugadores:
                            continue
                            
                        partida_id = self.jugadores[jugador_nick]['partida_id']
                        mensaje_chat = mensaje.get('message', '').strip()
                        
                        if mensaje_chat:
                            self.broadcast_partida(partida_id, {
                                "action": "chat_message",
                                "nickname": jugador_nick,
                                "message": mensaje_chat
                            })
                        
        except (json.JSONDecodeError, ConnectionResetError, BrokenPipeError, OSError):
            print(f"Cliente {direccion} ({jugador_nick or 'desconocido'}) desconectado.")
        except Exception as e:
            print(f"Error manejando cliente {direccion}: {e}")
        finally:
            if jugador_nick:
                self.remover_jugador(jugador_nick)
    
    def iniciar(self):
        self.server.bind((self.host, self.port))
        self.server.listen()
        print(f"🎮 Servidor de Juego escuchando en {self.host}:{self.port}")
        
        while True:
            try:
                cliente, direccion = self.server.accept()
                print(f"✅ Nueva conexión de juego desde {direccion}")
                
                hilo = threading.Thread(target=self.manejar_cliente, args=(cliente, direccion))
                hilo.daemon = True
                hilo.start()
            except Exception as e:
                print(f"Error aceptando conexión: {e}")

if __name__ == "__main__":
    game_server = GameServer()
    game_server.iniciar()