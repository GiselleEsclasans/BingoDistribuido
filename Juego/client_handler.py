import threading
import json
import time
from bingo_utils import generar_carton, verificar_patron_ganador, get_letter_for_number
from partida_manager import ManejadorPartida

class ClientHandler(threading.Thread):
    def __init__(self, cliente, direccion, server_instance):
        """
        Inicializa el hilo que maneja la conexión de un solo cliente.
        :param cliente: El objeto socket del cliente.
        :param direccion: La dirección (IP, puerto) del cliente.
        :param server_instance: La instancia principal de GameServer.
        """
        super().__init__(daemon=True)
        self.cliente = cliente
        self.direccion = direccion
        self.server = server_instance
        self.jugador_nick = None
        self.buffer = ""

    def run(self):
        """El bucle principal de escucha del cliente (antes era 'manejar_cliente')"""
        try:
            while True:
                datos = self.cliente.recv(1024).decode('utf-8')
                if not datos:
                    break
                
                self.buffer += datos
                
                while '\n' in self.buffer:
                    mensaje_str, self.buffer = self.buffer.split('\n', 1)
                    
                    if not mensaje_str:
                        continue
                        
                    try:
                        mensaje = json.loads(mensaje_str)
                    except json.JSONDecodeError:
                        print(f"Error: JSON malformado de {self.direccion}: {mensaje_str}")
                        continue

                    self.procesar_accion(mensaje)
                        
        except (ConnectionResetError, BrokenPipeError, OSError):
            print(f"Cliente {self.direccion} ({self.jugador_nick or 'desconocido'}) desconectado.")
        except Exception as e:
            print(f"Error manejando cliente {self.direccion}: {e}")
        finally:
            if self.jugador_nick:
                self.server.remover_jugador(self.jugador_nick)
            try:
                self.cliente.close()
            except:
                pass

    def procesar_accion(self, mensaje):
        """Revisa la 'action' del JSON y decide qué hacer."""
        action = mensaje.get('action')
        
        if action == 'join_game':
            self.handle_join_game(mensaje)
        
        elif action == 'call_bingo':
            self.handle_call_bingo(mensaje)
            
        elif action == 'chat_message':
            self.handle_chat_message(mensaje)

        elif action == 'mark_number':
            self.handle_mark_number(mensaje)

    def handle_join_game(self, mensaje):
        """Lógica para unir a un jugador a una partida."""
        self.jugador_nick = mensaje.get('nickname')
        jugadores = int(mensaje.get('players'))
        modo_juego = mensaje.get('game_mode')
        
        if not self.jugador_nick:
            return

        if self.jugador_nick in self.server.jugadores:
            self.server.remover_jugador(self.jugador_nick)

        partida_id = None
        for pid, pdata in self.server.partidas.items():
            if (pdata['max_jugadores'] == jugadores and
                pdata['modo_juego'] == modo_juego and
                len(pdata['jugadores']) < pdata['max_jugadores'] and
                pdata['activa']):
                partida_id = pid
                break

        if not partida_id:
            partida_id = f"partida_{modo_juego}_{jugadores}p_{time.time()}"
            self.server.partidas[partida_id] = {
                'id': partida_id,
                'max_jugadores': jugadores,
                'modo_juego': modo_juego,
                'jugadores': {},
                'numeros_salidos': [],
                'activa': True,
                'manager_started': False,
                'min_jugadores': 2
            }
            print(f"Creando nueva partida: {partida_id}")
            manejador = ManejadorPartida(partida_id, self.server)
            self.server.partidas[partida_id]['manager'] = manejador
        
        carton = generar_carton()
        self.server.partidas[partida_id]['jugadores'][self.jugador_nick] = {
            'carton': carton,
            'numeros_marcados': [] 
        }
        
        self.server.jugadores[self.jugador_nick] = {
            'socket': self.cliente,
            'partida_id': partida_id
        }
        
        partida = self.server.partidas[partida_id]

        if len(partida['jugadores']) >= 2 and not partida.get('manager_started', False):
            manejador = partida.get('manager')
            if manejador:
                try:
                    manejador.start()
                    partida['manager_started'] = True
                    print(f"Partida {partida_id} iniciada automáticamente por tener >=2 jugadores.")
                except RuntimeError:
                    # Si el hilo ya fue iniciado anteriormente, ignorar
                    print(f"Aviso: el manejador de {partida_id} ya fue iniciado.")

        respuesta = {
            "status": "success",
            "carton": carton,
            "partida_id": partida_id,
            "numeros_salidos": partida['numeros_salidos'],
            "numeros_salidos_labels": [f"{get_letter_for_number(n)}-{n}" for n in partida['numeros_salidos']]
        }
        self.send(respuesta)
        
        self.server.broadcast_partida(partida_id, {
            "action": "player_joined",
            "player": self.jugador_nick,
            "message": f"{self.jugador_nick} se unió!"
        })
        
        self.server.actualizar_lista_jugadores(partida_id)

    def handle_mark_number(self, mensaje):
        """Maneja cuando un cliente marca un número."""
        if not self.jugador_nick or self.jugador_nick not in self.server.jugadores:
            return
        
        partida_id = self.server.jugadores[self.jugador_nick].get('partida_id')
        if not partida_id or partida_id not in self.server.partidas:
            return
        
        partida = self.server.partidas[partida_id]
        datos_jugador = partida['jugadores'].get(self.jugador_nick)
        numero = mensaje.get('number')
        
        if not datos_jugador or numero is None:
            return
        
        if numero in datos_jugador['carton'] and numero in partida['numeros_salidos']:
            if numero not in datos_jugador['numeros_marcados']:
                datos_jugador['numeros_marcados'].append(numero)
                print(f"Jugador {self.jugador_nick} marcó el {numero}")
        else:
       
            print(f"WARN: {self.jugador_nick} intentó marcar un número inválido: {numero}")

    def handle_call_bingo(self, mensaje):
        """Lógica para cuando un jugador canta BINGO."""
        if not self.jugador_nick or self.jugador_nick not in self.server.jugadores:
            return
            
        partida_id = self.server.jugadores[self.jugador_nick]['partida_id']
        if partida_id not in self.server.partidas:
            return
            
        partida = self.server.partidas[partida_id]

        if not partida['activa']:
            return 
            
        datos_jugador = partida['jugadores'][self.jugador_nick]
        try:
            print(f"DEBUG: Verificando BINGO para {self.jugador_nick}")
            print(f"  Carton (len={len(datos_jugador.get('carton',[]))}): {datos_jugador.get('carton')}")
            print(f"  Numeros marcados en servidor: {datos_jugador.get('numeros_marcados')}")
            print(f"  Numeros salidos en partida: {partida.get('numeros_salidos')}")
        except Exception as e:
            print(f"DEBUG error al imprimir estado: {e}")

        if verificar_patron_ganador(datos_jugador['carton'],
                                    datos_jugador['numeros_marcados'],
                                    partida['modo_juego']):
            
            partida['activa'] = False 
            
            self.server.broadcast_partida(partida_id, {
                "action": "bingo_called",
                "winner": self.jugador_nick,
                "reason": f"BINGO!"
            })
            
            self.server.broadcast_partida(partida_id, {
                "action": "game_over",
                "winner": self.jugador_nick
            })
    
            self.server.cerrar_partida(partida_id)

        else:
            self.send({
                "action": "chat_message",
                "nickname": "Sistema",
                "message": "No tienes BINGO!"
            })

    def handle_chat_message(self, mensaje):
        """Lógica para retransmitir un mensaje de chat."""
        if not self.jugador_nick or self.jugador_nick not in self.server.jugadores:
            return
            
        partida_id = self.server.jugadores[self.jugador_nick]['partida_id']
        mensaje_chat = mensaje.get('message', '').strip()
        
        if mensaje_chat:
            self.server.broadcast_partida(partida_id, {
                "action": "chat_message",
                "nickname": self.jugador_nick,
                "message": mensaje_chat
            })

    def send(self, mensaje):
        """Método helper para enviar un mensaje a este cliente."""
        try:
            self.cliente.send((json.dumps(mensaje) + '\n').encode('utf-8'))
        except (BrokenPipeError, OSError):
            print(f"Error al enviar a {self.jugador_nick}, será removido.")
            self.server.remover_jugador(self.jugador_nick)