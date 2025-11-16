import pygame
from UI_manager import View

class UI_Configuraciones(View):
    def __init__(self, manager):
        super().__init__(manager)
    
        self.RED = tuple(int('a01515'[i:i+2], 16) for i in (0, 2, 4))
        self.YELLOW = tuple(int('ffa345'[i:i+2], 16) for i in (0, 2, 4))
        self.WHITE = (255, 255, 255)
        
        try:
            self.title_font = pygame.font.SysFont('Extenda', 48)
            self.option_font = pygame.font.SysFont('Extenda', 24)
            self.button_font = pygame.font.SysFont('Extenda', 26)
        except Exception:
            self.title_font = pygame.font.SysFont(None, 48)
            self.option_font = pygame.font.SysFont(None, 24)
            self.button_font = pygame.font.SysFont(None, 26)

        self.emoji_font = None
        for fname in ['Segoe UI Emoji', 'Noto Color Emoji', 'Apple Color Emoji']:
            try:
                f = pygame.font.SysFont(fname, 32)
                test = f.render('🔊', True, self.RED)
                if test.get_width() > 0:
                    self.emoji_font = f
                    break
            except Exception:
                continue
        
        self.use_graphic_fallback = self.emoji_font is None

        if not hasattr(self.manager, 'game_settings'):
            self.manager.game_settings = {
                'numero_jugadores': 4,
                'modo': 'regular' 
            }
        
        self.players_buttons = [2, 4, 6, 8]
        self.mode_buttons = ['Rápido', 'Regular', 'Blackout']
        
        self.music_enabled = True

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            back_rect = pygame.Rect(20, 20, 140, 48)
            if back_rect.collidepoint(mx, my):
                self.manager.set_view('bienvenida')
                return

            padding = 24
            inner_width = 560
            box_x = (800 - inner_width) // 2
            box_y = 140
            
            music_rect = pygame.Rect(box_x + inner_width - padding - 40, box_y + padding, 40, 40)
            if music_rect.collidepoint(mx, my):
                self.toggle_music()

            start_x = box_x + padding
            btn_y = box_y + padding + self.title_font.get_height() + 12 + self.option_font.get_height() + 8
            for i, count in enumerate(self.players_buttons):
                rect = pygame.Rect(start_x + i*80, btn_y, 60, 40)
                if rect.collidepoint(mx, my):
                    self.manager.game_settings['numero_jugadores'] = count

            mode_label_y = btn_y + 60
            btn_y2 = mode_label_y + self.option_font.get_height() + 8
            for i, mode in enumerate(self.mode_buttons):
                rect = pygame.Rect(box_x + padding + i*120, btn_y2, 100, 40)
                if rect.collidepoint(mx, my):
                    self.manager.game_settings['modo'] = mode.lower() 

    def toggle_music(self):
        """Activa o desactiva la música de fondo"""
        self.music_enabled = not self.music_enabled
        
        if self.music_enabled:
            pygame.mixer.music.unpause()
            if not pygame.mixer.music.get_busy():
                pygame.mixer.music.play(-1)
        else:
            pygame.mixer.music.pause()

    def render(self, surface):
        surface.fill(self.YELLOW)
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

        padding = 24
        inner_width = 560

        title_h = self.title_font.get_height()
        label_h = self.option_font.get_height()
        btn_h = 40

        inner_height = (padding * 2 + title_h + 12 + label_h + 8 + btn_h + 20 + label_h + 8 + btn_h)
        box_x = (800 - inner_width) // 2
        box_y = 140

        try:
            shadow = pygame.Surface((inner_width, inner_height), pygame.SRCALPHA)
            shadow.fill((0, 0, 0, 80))
            surface.blit(shadow, (box_x + 8, box_y + 8))
        except Exception:
            pygame.draw.rect(surface, (0, 0, 0), (box_x + 6, box_y + 6, inner_width, inner_height))

        try:
            pygame.draw.rect(surface, self.WHITE, pygame.Rect(box_x, box_y, inner_width, inner_height), border_radius=14)
        except Exception:
            pygame.draw.rect(surface, self.WHITE, (box_x, box_y, inner_width, inner_height))

        title = self.title_font.render('Configuraciones', True, self.RED)
        surface.blit(title, (box_x + padding, box_y + padding))

        music_rect = pygame.Rect(box_x + inner_width - padding - 40, box_y + padding, 40, 40)
        
        if not self.use_graphic_fallback:
            music_emoji = '🔊' if self.music_enabled else '🔇'
            music_text = self.emoji_font.render(music_emoji, True, self.RED)
            music_x = music_rect.x + (music_rect.w - music_text.get_width()) // 2
            music_y = music_rect.y + (music_rect.h - music_text.get_height()) // 2
            surface.blit(music_text, (music_x, music_y))
        else:
            if self.music_enabled:
                center_x, center_y = music_rect.centerx, music_rect.centery
                pygame.draw.circle(surface, self.RED, (center_x, center_y), 12, 2)
                pygame.draw.line(surface, self.RED, (center_x + 8, center_y - 8), (center_x + 15, center_y - 15), 2)
                pygame.draw.line(surface, self.RED, (center_x + 8, center_y + 8), (center_x + 15, center_y + 15), 2)
                pygame.draw.line(surface, self.RED, (center_x - 5, center_y - 5), (center_x - 5, center_y + 5), 2)
            else:
                center_x, center_y = music_rect.centerx, music_rect.centery
                pygame.draw.circle(surface, self.RED, (center_x, center_y), 12, 2)
                pygame.draw.line(surface, self.RED, (center_x - 8, center_y - 8), (center_x + 8, center_y + 8), 2)
                pygame.draw.line(surface, self.RED, (center_x - 8, center_y + 8), (center_x + 8, center_y - 8), 2)


        players_label = self.option_font.render('Número de Jugadores:', True, self.RED)
        label_x = box_x + padding
        label_y = box_y + padding + title.get_height() + 12
        surface.blit(players_label, (label_x, label_y))

        start_x = box_x + padding
        btn_y = label_y + players_label.get_height() + 8
        for i, count in enumerate(self.players_buttons):
            rect = pygame.Rect(start_x + i*80, btn_y, 60, btn_h)

            is_selected = self.manager.game_settings['numero_jugadores'] == count
            
            btn_color = self.RED if is_selected else self.YELLOW
            try:
                pygame.draw.rect(surface, btn_color, rect, border_radius=8)
            except Exception:
                pygame.draw.rect(surface, btn_color, rect)
            count_text = self.option_font.render(str(count), True, self.WHITE)
            count_x = rect.x + (rect.w - count_text.get_width()) // 2
            count_y = rect.y + (rect.h - count_text.get_height()) // 2
            surface.blit(count_text, (count_x, count_y))

        mode_label = self.option_font.render('Modo de Juego:', True, self.RED)
        mode_label_x = box_x + padding
        mode_label_y = btn_y + 60
        surface.blit(mode_label, (mode_label_x, mode_label_y))

        btn_y2 = mode_label_y + mode_label.get_height() + 8
        for i, mode in enumerate(self.mode_buttons):
            rect = pygame.Rect(box_x + padding + i*120, btn_y2, 100, btn_h)
            
            is_selected = self.manager.game_settings['modo'] == mode.lower() 
            
            btn_color = self.RED if is_selected else self.YELLOW
            try:
                pygame.draw.rect(surface, btn_color, rect, border_radius=8)
            except Exception:
                pygame.draw.rect(surface, btn_color, rect)
            mode_text = self.button_font.render(mode.capitalize(), True, self.WHITE)
            mode_x = rect.x + (rect.w - mode_text.get_width()) // 2
            mode_y = rect.y + (rect.h - mode_text.get_height()) // 2
            surface.blit(mode_text, (mode_x, mode_y))