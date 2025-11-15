import pygame
from UI_manager import View
import socket
import threading

class UI_Juego(View):
    def __init__(self, manager):
        super().__init__(manager)
      
        self.RED = tuple(int('a01515'[i:i+2], 16) for i in (0, 2, 4))
        self.YELLOW = tuple(int('ffa345'[i:i+2], 16) for i in (0, 2, 4))
        self.WHITE = (255, 255, 255)
        
        try:
            self.title_font = pygame.font.SysFont('Extenda', 24)
            self.chat_font = pygame.font.SysFont('Extenda', 18)
            self.button_font = pygame.font.SysFont('Extenda', 26)
        except Exception:
            self.title_font = pygame.font.SysFont(None, 24)
            self.chat_font = pygame.font.SysFont(None, 18)
            self.button_font = pygame.font.SysFont(None, 26)

        # Variables del chat
        self.chat_lines = []
        self.input_text = ''
        self.input_active = True
        
        # Cliente de chat
        self.chat_client = None
        self.nickname = "Jugador"  # Esto vendrá del registro
        
        # Estado de conexión
        self.conectado = False

    def conectar_chat(self, nickname, host='localhost', port=5000):
        """Conectar al servidor de chat cuando se inicia el juego"""
        self.nickname = nickname
        try:
            self.chat_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.chat_client.connect((host, port))
            
            # Enviar nickname al servidor
            self.chat_client.send(nickname.encode('utf-8'))
            
            # Iniciar hilo para recibir mensajes
            hilo_recepcion = threading.Thread(target=self.recibir_mensajes)
            hilo_recepcion.daemon = True
            hilo_recepcion.start()
            
            self.conectado = True
            self.agregar_mensaje_sistema(f"✅ Conectado como {nickname}")
            return True
            
        except Exception as e:
            print(f"❌ Error al conectar al chat: {e}")
            self.agregar_mensaje_sistema("❌ Error al conectar al servidor de chat")
            return False

    def recibir_mensajes(self):
        """Hilo para recibir mensajes del servidor"""
        while self.conectado:
            try:
                mensaje = self.chat_client.recv(1024).decode('utf-8')
                if mensaje:
                    # Formato esperado: "nickname: mensaje"
                    if ":" in mensaje:
                        nickname, texto = mensaje.split(":", 1)
                        self.agregar_mensaje_chat(nickname.strip(), texto.strip())
                    else:
                        self.agregar_mensaje_sistema(mensaje)
                else:
                    break
            except Exception as e:
                if self.conectado:
                    self.agregar_mensaje_sistema("🔌 Conexión perdida con el servidor")
                break

    def enviar_mensaje_chat(self, mensaje):
        """Enviar mensaje al servidor de chat"""
        if self.conectado and mensaje.strip():
            try:
                mensaje_completo = f"{self.nickname}: {mensaje.strip()}"
                self.chat_client.send(mensaje_completo.encode('utf-8'))
                # El mensaje propio se mostrará cuando llegue del servidor (broadcast)
            except Exception as e:
                self.agregar_mensaje_sistema("❌ Error al enviar mensaje")

    def agregar_mensaje_chat(self, quien, texto):
        """Agregar mensaje al historial del chat"""
        self.chat_lines.append((quien, texto))
        # Mantener máximo 20 líneas en el historial
        if len(self.chat_lines) > 20:
            self.chat_lines.pop(0)

    def agregar_mensaje_sistema(self, mensaje):
        """Agregar mensaje del sistema al chat"""
        self.chat_lines.append(("Sistema", mensaje))
        if len(self.chat_lines) > 20:
            self.chat_lines.pop(0)

    def desconectar_chat(self):
        """Desconectar del servidor de chat"""
        self.conectado = False
        if self.chat_client:
            try:
                self.chat_client.close()
            except:
                pass

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            back_rect = pygame.Rect(20, 20, 100, 48)
            if back_rect.collidepoint(mx, my):
                self.desconectar_chat()
                self.manager.set_view('bienvenida')
                return
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                if self.input_text.strip():
                    self.enviar_mensaje_chat(self.input_text.strip())
                    self.input_text = ''
            elif event.key == pygame.K_BACKSPACE:
                self.input_text = self.input_text[:-1]
            else:
                if event.unicode and len(self.input_text) < 50:  # Límite de caracteres
                    self.input_text += event.unicode

    def render(self, surface):
        surface.fill(self.YELLOW)
        
        # Botón Volver
        back_rect = pygame.Rect(20, 20, 100, 48)
        corner_radius = 12
        try:
            pygame.draw.rect(surface, self.WHITE, back_rect, border_radius=corner_radius)
        except Exception:
            pygame.draw.rect(surface, self.WHITE, back_rect)

        back_text = self.button_font.render('Volver', True, self.RED)
        back_x = back_rect.x + (back_rect.w - back_text.get_width()) // 2
        back_y = back_rect.y + (back_rect.h - back_text.get_height()) // 2
        surface.blit(back_text, (back_x, back_y))

        # Área de Juego
        game_rect = pygame.Rect(50, 80, 480, 320)
        try:
            shadow = pygame.Surface((game_rect.w, game_rect.h), pygame.SRCALPHA)
            shadow.fill((0, 0, 0, 80))
            surface.blit(shadow, (game_rect.x + 6, game_rect.y + 6))
        except Exception:
            pygame.draw.rect(surface, (0, 0, 0), (game_rect.x + 4, game_rect.y + 4, game_rect.w, game_rect.h))
        try:
            pygame.draw.rect(surface, self.WHITE, game_rect, border_radius=12)
        except Exception:
            pygame.draw.rect(surface, self.WHITE, game_rect)
        
        game_title = self.title_font.render('Área de Juego - Bingo', True, self.RED)
        surface.blit(game_title, (game_rect.x + (game_rect.w - game_title.get_width()) // 2,
                               game_rect.y + 10))

        # Área de Chat
        chat_rect = pygame.Rect(550, 80, 220, 320)
        try:
            shadow = pygame.Surface((chat_rect.w, chat_rect.h), pygame.SRCALPHA)
            shadow.fill((0, 0, 0, 80))
            surface.blit(shadow, (chat_rect.x + 6, chat_rect.y + 6))
        except Exception:
            pygame.draw.rect(surface, (0, 0, 0), (chat_rect.x + 4, chat_rect.y + 4, chat_rect.w, chat_rect.h))
        try:
            pygame.draw.rect(surface, self.WHITE, chat_rect, border_radius=12)
        except Exception:
            pygame.draw.rect(surface, self.WHITE, chat_rect)
        
        # Título del Chat con estado de conexión
        estado = "✅ Conectado" if self.conectado else "❌ Desconectado"
        chat_title = self.title_font.render(f'Chat ({estado})', True, self.RED)
        surface.blit(chat_title, (chat_rect.x + (chat_rect.w - chat_title.get_width()) // 2, 
                               chat_rect.y + 10))

        # Mostrar mensajes del chat (últimos 10)
        y = chat_rect.y + 40
        for quien, texto in self.chat_lines[-10:]:
            # Color diferente para mensajes del sistema
            color = (100, 100, 100) if quien == "Sistema" else self.RED
            chat_line = self.chat_font.render(f'{quien}: {texto}', True, color)
            
            # Truncar texto si es muy largo
            if len(texto) > 25:
                texto = texto[:25] + "..."
                
            chat_line = self.chat_font.render(f'{quien}: {texto}', True, color)
            surface.blit(chat_line, (chat_rect.x + 10, y))
            y += 20

        # Área de entrada de texto
        input_rect = pygame.Rect(50, 420, 720, 30)
        try:
            shadow = pygame.Surface((input_rect.w, input_rect.h), pygame.SRCALPHA)
            shadow.fill((0, 0, 0, 80))
            surface.blit(shadow, (input_rect.x + 4, input_rect.y + 4))
        except Exception:
            pygame.draw.rect(surface, (0, 0, 0), (input_rect.x + 2, input_rect.y + 2, input_rect.w, input_rect.h))
        
        # Cambiar color del input si está desconectado
        input_color = self.WHITE if self.conectado else (200, 200, 200)
        try:
            pygame.draw.rect(surface, input_color, input_rect, border_radius=8)
        except Exception:
            pygame.draw.rect(surface, input_color, input_rect)

        # Texto del input con placeholder si está vacío
        display_text = self.input_text if self.input_text else "Escribe un mensaje..." if self.conectado else "Desconectado"
        text_color = self.RED if self.input_text or not self.conectado else (150, 150, 150)
        
        input_text_surf = self.chat_font.render(display_text, True, text_color)
        text_height = input_text_surf.get_height()
        input_y = input_rect.y + (input_rect.height - text_height) // 2
        
        surface.blit(input_text_surf, (input_rect.x + 8, input_y))