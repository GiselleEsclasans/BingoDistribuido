import pygame
import emoji
import math

class JuegoRenderer:
    def __init__(self):
        self.VINOTINTO = tuple(int('a01515'[i:i+2], 16) for i in (0, 2, 4))
        self.YELLOW = tuple(int('ffa345'[i:i+2], 16) for i in (0, 2, 4))
        self.WHITE = (255, 255, 255)
        self.GREEN = (0, 150, 0)
        self.BLUE = (0, 100, 200)
        self.BLACK = (0, 0, 0)
        self.YELLOW_DARK = tuple(int('e6933e'[i:i+2], 16) for i in (0, 2, 4))
        self.TEXT_MUTED = (150, 150, 150)
        self.SHADOW_COLOR = (0, 0, 0, 80)
        self.CHAT_SISTEMA = (100, 100, 100)

        try:
            self.title_font = pygame.font.SysFont('Extenda', 24)
            self.chat_font = pygame.font.SysFont('Extenda', 18)
            self.button_font = pygame.font.SysFont('Extenda', 26)
            self.number_font = pygame.font.SysFont('Extenda', 20)
            self.bingo_font = pygame.font.SysFont('Extenda', 32)
            self.bingo_letter_font = pygame.font.SysFont('Extenda', 30, bold=True)
        except Exception:
            self.title_font = pygame.font.SysFont(None, 24)
            self.chat_font = pygame.font.SysFont(None, 18)
            self.button_font = pygame.font.SysFont(None, 26)
            self.number_font = pygame.font.SysFont(None, 20)
            self.bingo_font = pygame.font.SysFont(None, 32)
            self.bingo_letter_font = pygame.font.SysFont(None, 30, bold=True)
        
        self.emoji_font = None
        emoji_font_size = 18
        for fname in ['Segoe UI Emoji', 'Noto Color Emoji', 'Apple Color Emoji']:
            try:
                f = pygame.font.SysFont(fname, emoji_font_size)
                if f.render('😀', True, self.VINOTINTO).get_width() > 0:
                    self.emoji_font = f
                    print(f"✅ Fuente de Emoji encontrada: {fname}")
                    break
            except Exception:
                continue
        if not self.emoji_font:
            print("⚠️ No se encontró una fuente de emoji.")
            self.emoji_font = self.chat_font

        self.back_rect = pygame.Rect(20, 20, 100, 48)
        self.info_rect = pygame.Rect(140, 20, 640, 48)
        self.game_board_rect = pygame.Rect(50, 80, 480, 320)
        self.bingo_button_rect = pygame.Rect(50, 410, 150, 50)
        self.chat_rect = pygame.Rect(550, 80, 220, 320)
        self.input_rect = pygame.Rect(210, 420, 560, 30)

        self.carton_x_start = self.game_board_rect.x + 30
        self.carton_y_start = self.game_board_rect.y + 70
        self.cell_size = 38
        self.cell_margin = 4
        self.cell_radius = self.cell_size // 2

    def get_cell_at_pos(self, pos, state):
        """
        Comprueba si una posición (mx, my) está sobre un círculo del cartón.
        Devuelve el índice del número (0-24) o None si no se hizo clic.
        """
        if not state.juego_iniciado or not state.carton:
            return None
            
        mx, my = pos
        for i in range(5): 
            for j in range(5): 
                idx = i * 5 + j
                centro_x = self.carton_x_start + (j * (self.cell_size + self.cell_margin)) + self.cell_radius
                centro_y = self.carton_y_start + (i * (self.cell_size + self.cell_margin)) + self.cell_radius

                dist_x = mx - centro_x
                dist_y = my - centro_y
                if math.sqrt(dist_x**2 + dist_y**2) <= self.cell_radius:
                    return idx
        return None

    def draw_all(self, surface, state):
        """
        Dibuja la interfaz completa del juego basándose en el estado.
        :param surface: La superficie de Pygame (self.screen)
        :param state: La instancia de UI_Juego (self) que contiene el estado.
        """
        surface.fill(self.YELLOW)
        
        self._draw_info_bar(surface, state)
        self._draw_game_board(surface, state)
        self._draw_chat(surface, state)
        self._draw_buttons(surface, state)
        self._draw_input_bar(surface, state)

    def _draw_info_bar(self, surface, state):
        shadow = pygame.Surface((self.info_rect.w, self.info_rect.h), pygame.SRCALPHA)
        shadow.fill(self.SHADOW_COLOR)
        surface.blit(shadow, (self.info_rect.x + 4, self.info_rect.y + 4))
        pygame.draw.rect(surface, self.WHITE, self.info_rect, border_radius=12)
        modo_str = f"Modo: {state.modo_juego.upper()}"
        modo_surf = self.title_font.render(modo_str, True, self.VINOTINTO)
        modo_rect = modo_surf.get_rect(midleft = (self.info_rect.x + 20, self.info_rect.centery))
        surface.blit(modo_surf, modo_rect)
        jugadores_str = f"Jugadores: {len(state.online_players)} / {state.jugadores}"
        jugadores_surf = self.title_font.render(jugadores_str, True, self.VINOTINTO)
        jugadores_rect = jugadores_surf.get_rect(midright = (self.info_rect.right - 20, self.info_rect.centery))
        surface.blit(jugadores_surf, jugadores_rect)

    def _draw_game_board(self, surface, state):
        pygame.draw.rect(surface, self.VINOTINTO, self.game_board_rect, border_radius=12)

        letras = "BINGO"
        for i, letra in enumerate(letras):
            letra_surf = self.bingo_letter_font.render(letra, True, self.WHITE)
            letra_x = self.carton_x_start + (i * (self.cell_size + self.cell_margin)) + self.cell_radius
            letra_rect = letra_surf.get_rect(center=(letra_x, self.game_board_rect.y + 35))
            surface.blit(letra_surf, letra_rect)

        if state.carton and len(state.carton) == 25:
            for i in range(5):
                for j in range(5):
                    idx = i * 5 + j
                    numero = state.carton[idx]
                    
                    centro_x = self.carton_x_start + (j * (self.cell_size + self.cell_margin)) + self.cell_radius
                    centro_y = self.carton_y_start + (i * (self.cell_size + self.cell_margin)) + self.cell_radius
                    
                    if numero in state.numeros_marcados:
                        color_fondo, color_borde, color_texto = self.YELLOW, self.YELLOW_DARK, self.BLACK
                    else:
                        color_fondo, color_borde, color_texto = self.WHITE, self.YELLOW, self.VINOTINTO
                        
                    pygame.draw.circle(surface, color_fondo, (centro_x, centro_y), self.cell_radius)
                    pygame.draw.circle(surface, color_borde, (centro_x, centro_y), self.cell_radius, 3)
                    
                    num_text = self.number_font.render(str(numero), True, color_texto)
                    num_rect = num_text.get_rect(center=(centro_x, centro_y))
                    surface.blit(num_text, num_rect)

        numeros_x_start = self.game_board_rect.x + 260
        numeros_y_start = self.game_board_rect.y + 70
        titulo_surf = self.title_font.render('NÚMEROS SALIDOS', True, self.WHITE)
        titulo_rect = titulo_surf.get_rect(topleft=(numeros_x_start, self.game_board_rect.y + 30))
        surface.blit(titulo_surf, titulo_rect)
        
        for i, numero in enumerate(state.numeros_salidos[-25:]):
            num_text = self.number_font.render(str(numero), True, self.WHITE)
            fila, col = i // 5, i % 5
            num_x = numeros_x_start + col * 40
            num_y = numeros_y_start + fila * 30
            if num_y > self.game_board_rect.bottom - 30: break
            surface.blit(num_text, (num_x, num_y))

    def _draw_chat(self, surface, state):
        shadow = pygame.Surface((self.chat_rect.w, self.chat_rect.h), pygame.SRCALPHA)
        shadow.fill(self.SHADOW_COLOR)
        surface.blit(shadow, (self.chat_rect.x + 6, self.chat_rect.y + 6))
        pygame.draw.rect(surface, self.WHITE, self.chat_rect, border_radius=12)
        
        chat_title = self.title_font.render('Chat', True, self.VINOTINTO)
        surface.blit(chat_title, (self.chat_rect.x + (self.chat_rect.w - chat_title.get_width()) // 2, self.chat_rect.y + 10))

        y = self.chat_rect.y + 40
        padding_x = 10
        max_scroll = max(0, len(state.chat_lines) - state.chat_visible_lines)
        visible_lines = state.chat_lines[state.chat_scroll_offset : state.chat_scroll_offset + state.chat_visible_lines]
        
        for quien, texto in visible_lines:
            color = self.CHAT_SISTEMA if quien == "Sistema" else self.VINOTINTO
            prefix_surf = self.chat_font.render(f'{quien}: ', True, color)
            prefix_rect = prefix_surf.get_rect(topleft=(self.chat_rect.x + padding_x, y))
            if y > self.chat_rect.bottom - 20: break
            surface.blit(prefix_surf, prefix_rect)
            
            current_x = prefix_rect.right
            current_text_part = "" 
            for char in texto:
                if char in emoji.EMOJI_DATA:
                    if current_text_part:
                        text_surf = self.chat_font.render(current_text_part, True, color)
                        if current_x + text_surf.get_width() > self.chat_rect.right - padding_x: break 
                        surface.blit(text_surf, (current_x, y))
                        current_x += text_surf.get_width()
                        current_text_part = "" 
                    try:
                        emoji_surf = self.emoji_font.render(char, True, color)
                        if current_x + emoji_surf.get_width() > self.chat_rect.right - padding_x: break 
                        surface.blit(emoji_surf, (current_x, y))
                        current_x += emoji_surf.get_width()
                    except pygame.error: pass
                else:
                    current_text_part += char
            
            if current_text_part:
                text_surf = self.chat_font.render(current_text_part, True, color)
                if current_x + text_surf.get_width() <= self.chat_rect.right - padding_x:
                    surface.blit(text_surf, (current_x, y))
            y += 19
        
        if max_scroll > 0:
            scroll_text = ""
            if state.chat_scroll_offset > 0: scroll_text += "▲ " 
            if state.chat_scroll_offset < max_scroll: scroll_text += "▼" 
            if scroll_text:
                scroll_surf = self.chat_font.render(scroll_text, True, (0,0,0,100))
                scroll_rect = scroll_surf.get_rect(bottomright=(self.chat_rect.right - 10, self.chat_rect.bottom - 10))
                surface.blit(scroll_surf, scroll_rect)

    def _draw_buttons(self, surface, state):
        pygame.draw.rect(surface, self.WHITE, self.back_rect, border_radius=12)
        back_text = self.button_font.render('Volver', True, self.VINOTINTO)
        back_rect = back_text.get_rect(center=self.back_rect.center)
        surface.blit(back_text, back_rect)

        if state.puede_decir_bingo:
            pygame.draw.rect(surface, self.GREEN, self.bingo_button_rect, border_radius=10)
            bingo_text = self.bingo_font.render('BINGO!', True, self.WHITE)
            bingo_rect = bingo_text.get_rect(center=self.bingo_button_rect.center)
            surface.blit(bingo_text, bingo_rect)

    def _draw_input_bar(self, surface, state):
        shadow = pygame.Surface((self.input_rect.w, self.input_rect.h), pygame.SRCALPHA)
        shadow.fill(self.SHADOW_COLOR)
        surface.blit(shadow, (self.input_rect.x + 4, self.input_rect.y + 4))
        
        input_color = self.WHITE if state.juego_iniciado else (200, 200, 200)
        pygame.draw.rect(surface, input_color, self.input_rect, border_radius=8)
        
        display_text = state.input_text if state.input_text else "Escribe un mensaje..." if state.juego_iniciado else "Desconectado"
        text_color = self.VINOTINTO if state.input_text or not state.juego_iniciado else self.TEXT_MUTED
        
        input_text_surf = self.chat_font.render(display_text, True, text_color)
        text_rect = input_text_surf.get_rect(midleft = (self.input_rect.x + 10, self.input_rect.centery))
        surface.blit(input_text_surf, text_rect)