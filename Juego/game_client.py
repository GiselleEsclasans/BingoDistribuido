import socket
import threading
import json
import urllib.request
import urllib.error

class GameClient:
    def __init__(self, nickname, api_base_url, callbacks):
        """
        Maneja toda la comunicación de red para el cliente del juego.
        
        :param nickname: El nombre de usuario del jugador.
        :param api_base_url: La URL de la API (ej. http://localhost:8000).
        :param callbacks: Un diccionario de funciones para notificar a la UI.
        """
        self.nickname = nickname
        self.api_base_url = api_base_url
        self.callbacks = callbacks  
        
        self.socket = None
        self.buffer = ""
        self.is_running = False

    def connect(self, host, port, jugadores, modo_juego):
        """Intenta conectar al servidor del juego e iniciar la partida."""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((host, port))
    
            datos_inicio = {
                "action": "join_game",
                "nickname": self.nickname,
                "players": jugadores,
                "game_mode": modo_juego
            }
            self._send_json(datos_inicio)
            
            primera_respuesta = ""
            while '\n' not in primera_respuesta:
                self.socket.settimeout(5.0) 
                primera_respuesta += self.socket.recv(1024).decode('utf-8')
            
            self.socket.settimeout(None) 

            datos_str, _ = primera_respuesta.split('\n', 1)
            datos = json.loads(datos_str)

            if datos.get("status") == "success":
                self.is_running = True
                self.listen_thread = threading.Thread(target=self._listen_for_updates, daemon=True)
                self.listen_thread.start()
 
                self._set_api_online_status(True)
                return True, datos.get("carton"), datos.get("partida_id"), datos.get('numeros_salidos'), datos.get('numeros_salidos_labels')
            else:
                return False, None, None
                
        except socket.timeout:
            print("❌ Error: Timeout esperando la respuesta del servidor.")
            return False, None, None
        except Exception as e:
            print(f"❌ Error al conectar al cliente del juego: {e}")
            return False, None, None

    def _listen_for_updates(self):
        """Hilo para recibir actualizaciones del servidor de juego."""
        while self.is_running:
            try:
                datos = self.socket.recv(1024).decode('utf-8')
                if not datos:
                    if self.is_running:
                        print("Conexión perdida (servidor cerró).")
                    break 
                    
                self.buffer += datos
                
                while '\n' in self.buffer:
                    mensaje_str, self.buffer = self.buffer.split('\n', 1)
                    if not mensaje_str:
                        continue
                        
                    try:
                        mensaje = json.loads(mensaje_str)
                        self._process_server_message(mensaje)
                    except json.JSONDecodeError:
                        print(f"Error procesando JSON del servidor: {mensaje_str}")

            except Exception as e:
                if self.is_running:
                    print(f"Error en hilo de recepción: {e}")
                break
        
        self.is_running = False
        if self.callbacks.get('on_disconnect'):
            self.callbacks['on_disconnect']()

    def _process_server_message(self, mensaje):
        """Llama a la función callback apropiada según la acción del mensaje."""
        action = mensaje.get("action")
        
        if action == "number_drawn":
            if self.callbacks.get('on_number_drawn'):
                self.callbacks['on_number_drawn'](
                    mensaje.get("number"), 
                    mensaje.get("label")
                )
        
        elif action == "game_over":
            if self.callbacks.get('on_game_over'):
                self.callbacks['on_game_over'](mensaje.get("winner"))
        
        elif action == "chat_message":
            if self.callbacks.get('on_chat_message'):
                self.callbacks['on_chat_message'](mensaje.get("nickname"), mensaje.get("message"))
        
        elif action == "player_list":
             if self.callbacks.get('on_player_list'):
                self.callbacks['on_player_list'](mensaje.get("players", []))
        
        elif action == "player_joined":
             if self.callbacks.get('on_player_joined'):
                self.callbacks['on_player_joined'](mensaje.get("player"), mensaje.get("message"))
        
        elif action == "player_left":
             if self.callbacks.get('on_player_left'):
                self.callbacks['on_player_left'](mensaje.get("player"), mensaje.get("message"))
        
        elif action == "game_start":
             if self.callbacks.get('on_game_start'):
                self.callbacks['on_game_start'](mensaje.get("message"))

        elif action == "bingo_called":
             if self.callbacks.get('on_bingo_called'):
                self.callbacks['on_bingo_called'](mensaje.get("winner"), mensaje.get("reason"))
        

    def _send_json(self, data):
        """Método helper para enviar cualquier JSON al servidor."""
        
        if self.socket: 
            try:
                self.socket.send((json.dumps(data) + '\n').encode('utf-8'))
            except Exception as e:
                print(f"Error al enviar JSON: {e}")
                self.disconnect()

    def send_chat(self, message_text):
        """Envía un mensaje de chat al servidor."""
        if message_text:
            self._send_json({
                "action": "chat_message",
                "nickname": self.nickname,
                "message": message_text
            })

    def send_bingo(self):
        """Envía la acción 'call_bingo' al servidor."""
        print(f"¡{self.nickname} canta BINGO (enviando al servidor)!")
        self._send_json({"action": "call_bingo"})
    
    def send_mark_number(self, number):
        """Notifica al servidor que el jugador marcó un número."""
        self._send_json({
            "action": "mark_number",
            "number": number
        })

    def disconnect(self):
        """Desconecta al cliente del servidor y de la API."""
        if not self.is_running:
            return
            
        print(f"Desconectando {self.nickname}...")
        self.is_running = False
        
        self._set_api_online_status(False)
        
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
        self.socket = None

    def _set_api_online_status(self, online_status):
        """Actualiza el estado 'online' del jugador en la API REST."""
        try:
            data = json.dumps({"username": self.nickname, "online": online_status}).encode('utf-8')
            req = urllib.request.Request(
                f"{self.api_base_url}/set_online", 
                data=data, 
                headers={'Content-Type': 'application/json'}
            )
            urllib.request.urlopen(req, timeout=2)
        except Exception as e:
            print(f"Error al actualizar estado en API: {e}")