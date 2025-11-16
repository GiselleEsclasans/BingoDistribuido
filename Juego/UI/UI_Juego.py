import pygame
import random
import json
from UI_manager import View
import socket
import threading
from bingo_logic import BingoGame, get_pattern_description

class UI_Juego(View):
    def __init__(self, manager):
        super().__init__(manager)
      
        self.RED = tuple(int('a01515'[i:i+2], 16) for i in (0, 2, 4))
        self.YELLOW = tuple(int('ffa345'[i:i+2], 16) for i in (0, 2, 4))
        self.WHITE = (255, 255, 255)
        self.GREEN = (0, 150, 0)
        self.BLUE = (0, 100, 200)
        self.BLACK = (0, 0, 0)
        
        try:
            self.title_font = pygame.font.SysFont('Extenda', 24)
            self.chat_font = pygame.font.SysFont('Extenda', 18)
            self.button_font = pygame.font.SysFont('Extenda', 26)
            self.number_font = pygame.font.SysFont('Extenda', 20)
            self.bingo_font = pygame.font.SysFont('Extenda', 32)
        except Exception:
            self.title_font = pygame.font.SysFont(None, 24)
            self.chat_font = pygame.font.SysFont(None, 18)
            self.button_font = pygame.font.SysFont(None, 26)
            self.number_font = pygame.font.SysFont(None, 20)
            self.bingo_font = pygame.font.SysFont(None, 32)

        self.chat_lines = []
        self.input_text = ''
        self.input_active = True
        
        self.game_client = None
        self.nickname = "Jugador"
        
        self.conectado = False
        
        self.jugadores = 2
        self.modo_juego = "regular"
        self.bingo_game = None
        self.carton = []
        self.numeros_marcados = []
        self.numeros_salidos = []
        self.turno_actual = None
        self.ganador = None
        self.juego_iniciado = False
        self.puede_decir_bingo = False
        
        self.game_socket = None
        self.online_players = []

    def inicializar_juego(self, nickname, jugadores, modo_juego, host='localhost', port=6000, api_base_url='http://localhost:8000'):
        """Conectar al servidor de juego y configurar partida"""
        self.nickname = nickname
        self.jugadores = jugadores
        self.modo_juego = modo_juego
        
        try:
            self.game_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.game_socket.connect((host, port))
            
            datos_inicio = {
                "action": "join_game",
                "nickname": nickname,
                "players": jugadores,
                "game_mode": modo_juego
            }
            
            mensaje_enviar = json.dumps(datos_inicio) + '\n'
            self.game_socket.send(mensaje_enviar.encode('utf-8'))
            

            respuesta_bytes = self.game_socket.recv(1024)
            respuesta = respuesta_bytes.decode('utf-8').strip() 
            if not respuesta:
                 raise Exception("Respuesta vacía del servidor")
                 
            datos = json.loads(respuesta)
            
            if datos.get("status") == "success":
                self.carton = datos.get("carton", [])
                
                self.inicializar_bingo_logic()
                
                try:
                    self.online_players = datos.get('players', []) or []
                except Exception:
                    self.online_players = []
                    
                self.juego_iniciado = True
                self.agregar_mensaje_sistema("🎮 Partida iniciada! Tu cartón está listo.")
                
                hilo_juego = threading.Thread(target=self.recibir_actualizaciones_juego)
                hilo_juego.daemon = True
                hilo_juego.start()
                
                try:
                    import urllib.request, urllib.error
                    data = json.dumps({"username": self.nickname, "online": True}).encode('utf-8')
                    req = urllib.request.Request(f"{api_base_url}/set_online", data=data, headers={'Content-Type': 'application/json'})
                    urllib.request.urlopen(req, timeout=2)
                except Exception:
                    pass
                
                return True
            else:
                self.agregar_mensaje_sistema("❌ Error al unirse a la partida")
                return False
                
        except Exception as e:
            print(f"❌ Error al conectar al juego: {e}")
            self.agregar_mensaje_sistema("❌ Error al conectar al servidor de juego")
            return False

    def inicializar_bingo_logic(self):
        """Inicializar la lógica del juego Bingo"""
        try:
            self.bingo_game = BingoGame(
                player_name=self.nickname,
                game_mode=self.modo_juego,
                players_count=self.jugadores
            )
            if self.carton:
                self.bingo_game.card = self.carton
            print(f"✅ Lógica del Bingo inicializada con cartón de {len(self.carton)} números")
        except Exception as e:
            print(f"❌ Error al inicializar lógica del Bingo: {e}")
            self.bingo_game = None

    def recibir_actualizaciones_juego(self):
        """Hilo para recibir actualizaciones del servidor de juego"""
        buffer = ""
        while self.juego_iniciado:
            try:
                datos = self.game_socket.recv(1024).decode('utf-8')
                if not datos:
                    break
                    
                buffer += datos

                while '\n' in buffer:
                    mensaje_str, buffer = buffer.split('\n', 1)
                    
                    if not mensaje_str:
                        continue
                        
                    try:
                        mensaje = json.loads(mensaje_str)
                        self.procesar_mensaje_juego(mensaje)
                    except json.JSONDecodeError:
                        print(f"Error procesando JSON del servidor: {mensaje_str}")

            except Exception as e:
                if self.juego_iniciado:
                    self.agregar_mensaje_sistema("🔌 Conexión perdida con el servidor de juego")
                    print(f"Error en hilo de recepción: {e}")
                break
                
        self.juego_iniciado = False
        self.agregar_mensaje_sistema("🔌 Desconectado.")

    def procesar_mensaje_juego(self, mensaje):
        """Procesar mensajes recibidos del servidor de juego"""
        action = mensaje.get("action")
        
        if action == "number_drawn":
            numero = mensaje.get("number")
            self.numeros_salidos.append(numero)
            
            if numero in self.carton and numero not in self.numeros_marcados:
                self.numeros_marcados.append(numero)
                
                if self.bingo_game:
                    self.bingo_game.mark_number(numero)
                    self.verificar_patron_ganador()
                
        elif action == "player_turn":
            self.turno_actual = mensaje.get("player")
                
        elif action == "bingo_called":
            ganador = mensaje.get("winner")
            motivo = mensaje.get("reason")
            self.ganador = ganador
            self.agregar_mensaje_sistema(f"🏆 {ganador} dice BINGO! ({motivo})")
            self.puede_decir_bingo = False
            
        elif action == "game_over":
            self.juego_iniciado = False
            ganador = mensaje.get("winner")
            self.agregar_mensaje_sistema(f"🎉 ¡Juego terminado! Ganador: {ganador}")
        
        elif action == "chat_message":
            nick = mensaje.get('nickname')
            texto = mensaje.get('message')
            self.agregar_mensaje_chat(nick, texto)

        elif action == "player_joined":
            nick = mensaje.get('player')
            if nick and nick not in self.online_players:
                self.online_players.append(nick)
            self.agregar_mensaje_sistema(mensaje.get('message', f"{nick} se unió"))

        elif action == "player_list":
            players = mensaje.get('players') or []
            try:
                self.online_players = list(players)
            except Exception:
                self.online_players = []

        elif action == "player_left":
            nick = mensaje.get('player')
            if nick and nick in self.online_players:
                try:
                    self.online_players.remove(nick)
                except ValueError:
                    pass
            self.agregar_mensaje_sistema(mensaje.get('message', f"{nick} abandonó"))

        elif action == "game_start":
            self.agregar_mensaje_sistema(mensaje.get('message', 'La partida ha comenzado'))

    def verificar_patron_ganador(self):
        """Verificar si el jugador tiene un patrón ganador usando bingo_logic"""
        if not self.bingo_game:
            print("Error: Verificando patrón sin bingo_game inicializado.")
            return
        
        if self.bingo_game.check_winning_condition():
            if not self.ganador:
                self.puede_decir_bingo = True
                pattern_name = self.bingo_game.winning_pattern_name
                pattern_desc = get_pattern_description(pattern_name, self.modo_juego)
                self.agregar_mensaje_sistema(f"🎉 ¡Tienes {pattern_desc}! Presiona BINGO")

    def dibujar_carton(self, surface, x, y):
        """Dibujar el cartón de bingo en la pantalla"""
        if not self.carton or len(self.carton) != 25: 
            if self.carton:
                 print(f"Error: El cartón tiene {len(self.carton)} números, se esperaban 25.")
            return
            
        celda_size = 35 
        margen = 2
        
        titulo = self.title_font.render('TU CARTÓN', True, self.RED)
        surface.blit(titulo, (x, y - 30))
        
        for i in range(5): 
            for j in range(5):
                idx = i * 5 + j
                numero = self.carton[idx]
                
                rect_x = x + j * (celda_size + margen)
                rect_y = y + i * (celda_size + margen)
                celda_rect = pygame.Rect(rect_x, rect_y, celda_size, celda_size)
                
                if numero in self.numeros_marcados:
                    color_fondo = self.GREEN
                    color_texto = self.WHITE
                else:
                    color_fondo = self.WHITE
                    color_texto = self.RED
                    
                pygame.draw.rect(surface, color_fondo, celda_rect)
                pygame.draw.rect(surface, self.RED, celda_rect, 2)
                
                num_text = self.number_font.render(str(numero), True, color_texto)
                num_x = rect_x + (celda_size - num_text.get_width()) // 2
                num_y = rect_y + (celda_size - num_text.get_height()) // 2
                surface.blit(num_text, (num_x, num_y))

    def dibujar_numeros_salidos(self, surface, x, y):
        """Dibujar los números que han salido"""
        titulo = self.title_font.render('NÚMEROS SALIDOS', True, self.RED)
        surface.blit(titulo, (x, y - 30))
        
        numeros_recientes = self.numeros_salidos[-15:]
        for i, numero in enumerate(numeros_recientes):
            num_text = self.number_font.render(str(numero), True, self.BLUE)
            fila = i // 5
            col = i % 5
            surface.blit(num_text, (x + col * 40, y + fila * 30))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            
            back_rect = pygame.Rect(20, 20, 100, 48)
            if back_rect.collidepoint(mx, my):
                self.desconectar_juego()
                self.manager.set_view('bienvenida')
                return
                
            if self.puede_decir_bingo:
                bingo_rect = pygame.Rect(50, 410, 150, 50)
                if bingo_rect.collidepoint(mx, my):
                    self.decir_bingo()
                    self.puede_decir_bingo = False 
    
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                if self.input_text.strip():
                    self.enviar_mensaje_chat(self.input_text.strip())
                    self.input_text = ''
            elif event.key == pygame.K_BACKSPACE:
                self.input_text = self.input_text[:-1]
            else:
                if event.unicode and len(self.input_text) < 50:
                    self.input_text += event.unicode

    def decir_bingo(self):
        """Enviar 'call_bingo' al servidor"""
        if not self.juego_iniciado:
            return
            
        print(f"¡{self.nickname} canta BINGO!")
        try:
            mensaje_bingo = {
                "action": "call_bingo"
            }
            self.game_socket.send((json.dumps(mensaje_bingo) + '\n').encode('utf-8'))
        except Exception as e:
            self.agregar_mensaje_sistema("❌ Error al cantar BINGO")
            print(f"Error en decir_bingo: {e}")

    def enviar_mensaje_chat(self, mensaje):
        """Enviar mensaje al chat (usando el mismo socket del juego)"""
        if self.juego_iniciado and mensaje.strip():
            try:
                mensaje_chat = {
                    "action": "chat_message",
                    "nickname": self.nickname,
                    "message": mensaje.strip()
                }
                self.game_socket.send((json.dumps(mensaje_chat) + '\n').encode('utf-8'))
            except Exception as e:
                self.agregar_mensaje_sistema("❌ Error al enviar mensaje")

    def agregar_mensaje_chat(self, quien, texto):
        """Agregar mensaje al historial del chat"""
        self.chat_lines.append((quien, texto))
        if len(self.chat_lines) > 20:
            self.chat_lines.pop(0)

    def agregar_mensaje_sistema(self, mensaje):
        """Agregar mensaje del sistema al chat"""
        self.chat_lines.append(("Sistema", mensaje))
        if len(self.chat_lines) > 20:
            self.chat_lines.pop(0)

    def desconectar_juego(self):
        """Desconectar del servidor de juego"""
        self.juego_iniciado = False
        try:
            import urllib.request, urllib.error
            data = json.dumps({"username": self.nickname, "online": False}).encode('utf-8')
            req = urllib.request.Request(f"http://localhost:8000/set_online", data=data, headers={'Content-Type': 'application/json'})
            urllib.request.urlopen(req, timeout=1)
        except Exception:
            pass

        if self.game_socket:
            try:
                self.game_socket.close()
            except:
                pass
        
        self.carton = []
        self.numeros_marcados = []
        self.numeros_salidos = []
        self.ganador = None
        self.puede_decir_bingo = False
        self.chat_lines = []

    def render(self, surface):
        surface.fill(self.YELLOW)
        
        back_rect = pygame.Rect(20, 20, 100, 48)
        pygame.draw.rect(surface, self.WHITE, back_rect, border_radius=12)
        back_text = self.button_font.render('Volver', True, self.RED)
        back_x = back_rect.x + (back_rect.w - back_text.get_width()) // 2
        back_y = back_rect.y + (back_rect.h - back_text.get_height()) // 2
        surface.blit(back_text, (back_x, back_y))

        game_rect = pygame.Rect(50, 80, 480, 320)
        shadow = pygame.Surface((game_rect.w, game_rect.h), pygame.SRCALPHA)
        shadow.fill((0, 0, 0, 80))
        surface.blit(shadow, (game_rect.x + 6, game_rect.y + 6))
        pygame.draw.rect(surface, self.WHITE, game_rect, border_radius=12)
        
        game_title = self.title_font.render('BINGO - Modo: ' + self.modo_juego.upper(), True, self.RED)
        surface.blit(game_title, (game_rect.x + (game_rect.w - game_title.get_width()) // 2, game_rect.y + 10))

        carton_x = game_rect.x + 20
        carton_y = game_rect.y + 50
        self.dibujar_carton(surface, carton_x, carton_y)
        
        numeros_x = game_rect.x + 230
        numeros_y = game_rect.y + 50
        self.dibujar_numeros_salidos(surface, numeros_x, numeros_y)
        
        info_y = game_rect.y + 250 
        info_text_str = f'Jugadores: {len(self.online_players)}/{self.jugadores} | Turno: {self.turno_actual or "..."}'
        info_text = self.chat_font.render(info_text_str, True, self.RED)
        surface.blit(info_text, (game_rect.x + 20, info_y))
        
        if self.puede_decir_bingo:
            bingo_rect = pygame.Rect(50, 410, 150, 50) 
            pygame.draw.rect(surface, self.GREEN, bingo_rect, border_radius=10)
            bingo_text = self.bingo_font.render('BINGO!', True, self.WHITE)
            bingo_x = bingo_rect.x + (bingo_rect.w - bingo_text.get_width()) // 2
            bingo_y = bingo_rect.y + (bingo_rect.h - bingo_text.get_height()) // 2
            surface.blit(bingo_text, (bingo_x, bingo_y))

        chat_rect = pygame.Rect(550, 80, 220, 320)
        shadow = pygame.Surface((chat_rect.w, chat_rect.h), pygame.SRCALPHA)
        shadow.fill((0, 0, 0, 80))
        surface.blit(shadow, (chat_rect.x + 6, chat_rect.y + 6))
        pygame.draw.rect(surface, self.WHITE, chat_rect, border_radius=12)
        
        estado = "✅ Conectado" if self.juego_iniciado else "❌ Desconectado"
        chat_title = self.title_font.render(f'Chat ({estado})', True, self.RED)
        surface.blit(chat_title, (chat_rect.x + (chat_rect.w - chat_title.get_width()) // 2, chat_rect.y + 10))

        y = chat_rect.y + 40
        for quien, texto in self.chat_lines[-12:]:
            color = (100, 100, 100) if quien == "Sistema" else self.RED
            linea_chat = f'{quien}: {texto}'
            if len(linea_chat) > 28:
                linea_chat = linea_chat[:28] + "..."
            
            chat_line_surf = self.chat_font.render(linea_chat, True, color)
            surface.blit(chat_line_surf, (chat_rect.x + 10, y))
            y += 19 

        input_rect = pygame.Rect(210, 420, 560, 30) 
        shadow = pygame.Surface((input_rect.w, input_rect.h), pygame.SRCALPHA)
        shadow.fill((0, 0, 0, 80))
        surface.blit(shadow, (input_rect.x + 4, input_rect.y + 4))
        
        input_color = self.WHITE if self.juego_iniciado else (200, 200, 200)
        pygame.draw.rect(surface, input_color, input_rect, border_radius=8)

        display_text = self.input_text if self.input_text else "Escribe un mensaje..." if self.juego_iniciado else "Desconectado"
        text_color = self.RED if self.input_text or not self.juego_iniciado else (150, 150, 150)
        
        input_text_surf = self.chat_font.render(display_text, True, text_color)
        text_height = input_text_surf.get_height()
        input_y = input_rect.y + (input_rect.height - text_height) // 2
        surface.blit(input_text_surf, (input_rect.x + 8, input_y))