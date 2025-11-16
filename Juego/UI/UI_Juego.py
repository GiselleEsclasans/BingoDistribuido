import pygame
import json
from UI_manager import View
from bingo_logic import BingoGame, get_pattern_description
from game_client import GameClient
import emoji 
import math 

from UI.ui_juego_renderer import JuegoRenderer

class UI_Juego(View):
    def __init__(self, manager):
        super().__init__(manager)
      
        self.renderer = JuegoRenderer()
        
        self.chat_lines = []
        self.input_text = ''
        self.nickname = "Jugador"
        self.jugadores = 2
        self.modo_juego = "regular"
        self.bingo_game = None
        self.carton = []
        self.numeros_marcados = []
        self.numeros_salidos = []
        self.ganador = None
        self.juego_iniciado = False
        self.puede_decir_bingo = False
        self.online_players = []
        self.client = None

        self.chat_scroll_offset = 0 
        self.chat_visible_lines = 12
        
    def inicializar_juego(self, nickname, jugadores, modo_juego, host='localhost', port=6000, api_base_url='http://localhost:8000'):
        """Conectar al servidor de juego y configurar partida"""
        self._reset_game_state()
        
        self.nickname = nickname
        self.jugadores = jugadores
        self.modo_juego = modo_juego
        
        callbacks = {
            'on_number_drawn': self._on_number_drawn,
            'on_game_over': self._on_game_over,
            'on_chat_message': self._on_chat_message,
            'on_player_list': self._on_player_list,
            'on_player_joined': self._on_player_joined,
            'on_player_left': self._on_player_left,
            'on_game_start': self._on_game_start,
            'on_bingo_called': self._on_bingo_called,
            'on_disconnect': self._on_disconnect,
        }

        self.client = GameClient(self.nickname, api_base_url, callbacks)
        success, carton, partida_id = self.client.connect(host, port, jugadores, modo_juego)

        if success:
            self.carton = carton or []
            self.juego_iniciado = True
            
            self.inicializar_bingo_logic()
            self.agregar_mensaje_sistema("🎮 Partida iniciada! Tu cartón está listo.")
            return True
        else:
            self.agregar_mensaje_sistema("❌ Error al conectar al servidor de juego")
            self.client = None
            return False
            
    def _reset_game_state(self):
        """Limpia todas las variables de estado del juego."""
        self.carton = []
        self.numeros_marcados = []
        self.numeros_salidos = []
        self.ganador = None
        self.puede_decir_bingo = False
        self.chat_lines = []
        self.online_players = []
        self.juego_iniciado = False
        self.chat_scroll_offset = 0
        if self.client:
            self.client.disconnect()
            self.client = None

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

    
    def _on_number_drawn(self, numero):
        self.numeros_salidos.append(numero)
        self.agregar_mensaje_sistema(f"🎲 Número sorteado: {numero}")
        
    def _on_bingo_called(self, ganador, motivo):
        self.ganador = ganador
        self.agregar_mensaje_sistema(f"🏆 {ganador} dice BINGO! ({motivo})")
        self.puede_decir_bingo = False
        
    def _on_game_over(self, ganador):
        self.juego_iniciado = False
        self.agregar_mensaje_sistema(f"🎉 ¡Juego terminado! Ganador: {ganador}")
        
    def _on_chat_message(self, nick, texto):
        self.agregar_mensaje_chat(nick, texto)
        
    def _on_player_joined(self, nick, message):
        if nick and nick not in self.online_players:
            self.online_players.append(nick)
        self.agregar_mensaje_sistema(message or f"{nick} se unió")

    def _on_player_list(self, players):
        try:
            self.online_players = list(players)
        except Exception:
            self.online_players = []
            
    def _on_player_left(self, nick, message):
        if nick and nick in self.online_players:
            try:
                self.online_players.remove(nick)
            except ValueError:
                pass
        self.agregar_mensaje_sistema(message or f"{nick} abandonó")

    def _on_game_start(self, message):
        self.agregar_mensaje_sistema(message or 'La partida ha comenzado')
        
    def _on_disconnect(self):
        self.juego_iniciado = False
        self.agregar_mensaje_sistema("🔌 Desconectado.")

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
    
    def _on_cell_clicked(self, numero):
        """
        Maneja la lógica cuando el jugador hace clic en un número del cartón.
        """
        if not self.juego_iniciado or not self.bingo_game:
            return
            
        if numero in self.numeros_marcados:
            return
        
        if numero in self.numeros_salidos:
            self.numeros_marcados.append(numero)
            self.bingo_game.mark_number(numero)
            self.verificar_patron_ganador()
        else:
            self.agregar_mensaje_sistema(f"¡Aún no ha salido el {numero}!")
    
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEWHEEL:
            mx, my = pygame.mouse.get_pos()
            if self.renderer.chat_rect.collidepoint(mx, my):
                self.chat_scroll_offset -= event.y
                max_scroll = max(0, len(self.chat_lines) - self.chat_visible_lines)
                self.chat_scroll_offset = max(0, min(self.chat_scroll_offset, max_scroll))
                return

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            
            if self.renderer.back_rect.collidepoint(mx, my):
                self.desconectar_juego()
                self.manager.set_view('bienvenida')
                return
                
            if self.puede_decir_bingo:
                if self.renderer.bingo_button_rect.collidepoint(mx, my):
                    self.decir_bingo()
                    self.puede_decir_bingo = False 
                    return 

            cell_index = self.renderer.get_cell_at_pos((mx, my), self)
            if cell_index is not None:
                numero_clicado = self.carton[cell_index]
                self._on_cell_clicked(numero_clicado)
                return
    
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

    #METODOS DE ENVÍO
    
    def decir_bingo(self):
        """Enviar 'call_bingo' al servidor."""
        if self.client:
            self.client.send_bingo()

    def enviar_mensaje_chat(self, mensaje):
        """Enviar mensaje al chat."""
        if self.client and mensaje.strip():
            self.client.send_chat(mensaje.strip())

    def desconectar_juego(self):
        """Desconecta al cliente y resetea el estado de la UI."""
        self._reset_game_state()

    #METODOS DE CHAT

    def agregar_mensaje_chat(self, quien, texto):
        """Agregar mensaje al historial del chat"""
        self.chat_lines.append((quien, texto))
        self._scroll_to_bottom() 

    def agregar_mensaje_sistema(self, mensaje):
        """Agregar mensaje del sistema al chat"""
        self.chat_lines.append(("Sistema", mensaje))
        self._scroll_to_bottom() 
        
    def _scroll_to_bottom(self):
        """Mueve el scroll al último mensaje."""
        self.chat_scroll_offset = max(0, len(self.chat_lines) - self.chat_visible_lines)


    def render(self, surface):
        """
        Llama al renderer para dibujar la UI completa,
        pasándole 'self' como el objeto de estado.
        """
        self.renderer.draw_all(surface, self)